#include "Python.h"

#ifdef MS_WINDOWS
#include "osdefs.h"
#elif defined(__CYGWIN__)
#include <windows.h>
#include <sys/cygwin.h>
#endif

#define SCRIPT_TAG 0x1234567A

struct script_info {
  int tag;
  int offset;
};

struct script_data {
  int tag;
  int length;
};

static int _system_error(char *filename, int lineno, char *where)
{
  fprintf(stderr, "%s:%d: In %s, %s\n",
          filename, lineno, where, strerror(errno));
  return errno;
}

#define system_error(where) _system_error(__FILE__, __LINE__, where)

static int print_error(char *msg)
{
  fputs(msg, stderr);
  fputc('\n', stderr);
  return 1;
}

#ifdef MS_WINDOWS
static void fixup_syspath(char *path, int delim)
{
  char *p, *new_path;

  new_path = path;
  for (;;) {
    /* skip empty path segments */
    while (*path == delim) path++;

    p = strchr(path, delim);
    if (p == NULL) {
      /* copy the remaining path */
      while (*path) *new_path++ = *path++;
      *new_path = '\0';
      break;
    }

    /* copy over the segment including delimiter */
    while (path <= p) *new_path++ = *path++;
  }
}
#endif /* def MS_WINDOWS */

int main(int argc, char **argv)
{
  int result;
  char *filename;
  FILE *script_file;
  struct script_info si;
  struct script_data sd;
  char *script;
#ifdef __CYGWIN__
  DWORD rc;
  struct external_pinfo pinfo;
#endif

  Py_SetProgramName(argv[0]);

  /* Let Python determine the full path for the executable */
  filename = Py_GetProgramFullPath();
#ifdef MS_WINDOWS
  /* Fixup broken sys.path on Windows */
  fixup_syspath(Py_GetPath(), DELIM);
#endif

  /* Open the executable file for reading */
  if ((script_file = fopen(filename, "rb")) == NULL)
    return system_error("fopen");

  /* Move to location of script_info in the executable */
  if (fseek(script_file, -((long) sizeof(si)), SEEK_END) != 0) {
    fclose(script_file);
    return system_error("fseek(EOF)");
  }

  /* Read the script_info structure */
  if (fread((void *)&si, sizeof(si), 1, script_file) != 1) {
    fclose(script_file);
    return system_error("fread(script_info)");
  }

  /* Verify script_info structure */
  if (si.tag != SCRIPT_TAG) {
    fclose(script_file);
    return print_error("Executable invalid or damaged.");
  }

  /* Move to location of script_data in the executable */
  if (fseek(script_file, si.offset, SEEK_SET) != 0) {
    fclose(script_file);
    return system_error("fseek(script_info.offset)");
  }

  /* Read the script_data structure */
  if (fread((void *)&sd, sizeof(sd), 1, script_file) != 1) {
    fclose(script_file);
    return system_error("fread(script_data)");
  }

  /* Verify script_data structure */
  if (sd.tag != SCRIPT_TAG) {
    fclose(script_file);
    return print_error("Executable invalid or damaged.");
  }

  /* Allocate the buffer for the script data */
  if ((script = (char *) malloc(sd.length + 1)) == NULL) {
    fclose(script_file);
    return print_error("Out of memory.");
  }

  /* Read the actual script */
  if (fread((void *)script, sd.length, 1, script_file) != 1) {
    free(script);
    fclose(script_file);
    return system_error("fread(script)");
  }

  /* Null-terminate the script */
  script[sd.length] = '\0';

  /* Done with the executable file */
  fclose(script_file);

  /* Run it! */
  Py_Initialize();
  PySys_SetArgv(argc, argv);
  result = PyRun_SimpleString(script);
  Py_Finalize();

  free(script);

  return result;
}
