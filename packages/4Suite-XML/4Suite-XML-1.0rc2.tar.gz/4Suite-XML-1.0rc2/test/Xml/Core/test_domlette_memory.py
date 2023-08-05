import gc
from Ft.Xml import InputSource

def test_empty_node(tester,domMod):

    tester.startTest("Empty Document")
    domMod.StartNodeCounting()
    doc = domMod.implementation.createDocument(None,None,None)
    tester.compare(1,domMod.GetNodeCount())
    del doc
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Text")
    domMod.StartNodeCounting()
    doc = domMod.implementation.createDocument(None,None,None)
    text = doc.createTextNode("Foo")
    tester.compare(2,domMod.GetNodeCount())
    del text
    tester.compare(1,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Element")
    domMod.StartNodeCounting()
    elem = doc.createElementNS(None,"Foo")
    tester.compare(1,domMod.GetNodeCount())
    del elem
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Attribute")
    domMod.StartNodeCounting()
    attr = doc.createAttributeNS(None,"Foo")
    tester.compare(1,domMod.GetNodeCount())
    del attr
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Comment")
    domMod.StartNodeCounting()
    com = doc.createComment("Foo")
    tester.compare(1,domMod.GetNodeCount())
    del com
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Processing Instruction")
    domMod.StartNodeCounting()
    pi = doc.createProcessingInstruction("Foo","Bar")
    tester.compare(1,domMod.GetNodeCount())
    del pi
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Empty Document Fragment")
    domMod.StartNodeCounting()
    df = doc.createDocumentFragment()
    tester.compare(1,domMod.GetNodeCount())
    del df
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()


def test_small_tree(tester,domMod):
    import sys, gc
    gc.collect()  #Force to clean everything up
    tester.startTest("Single Parent -> child rel")
    doc = domMod.implementation.createDocument(None,None,None)
    domMod.StartNodeCounting()
    elem = doc.createElementNS(None,"Foo")
    elem2 = doc.createElementNS(None,"Foo2")
    elem.appendChild(elem2)
    tester.compare(2,domMod.GetNodeCount())
    del elem
    del elem2
    gc.collect() #Force collection
    tester.compare(0,domMod.GetNodeCount())
    del doc
    tester.testDone()

    tester.startTest("Document -> elem rel")
    domMod.StartNodeCounting()
    doc = domMod.implementation.createDocument(None,None,None)
    elem = doc.createElementNS(None,"Foo")
    doc.appendChild(elem)
    tester.compare(2,domMod.GetNodeCount())
    del doc
    del elem
    gc.collect() #Force collection
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Document -> text rel")
    domMod.StartNodeCounting()
    doc = domMod.implementation.createDocument(None,None,None)
    text = doc.createTextNode("Foo")
    doc.appendChild(text)
    tester.compare(2,domMod.GetNodeCount())
    del doc
    del text
    gc.collect() #Force collection
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Document -> pi rel")
    domMod.StartNodeCounting()
    doc = domMod.implementation.createDocument(None,None,None)
    pi = doc.createProcessingInstruction("Foo","Bar")
    doc.appendChild(pi)
    tester.compare(2,domMod.GetNodeCount())
    del doc
    del pi
    gc.collect() #Force collection
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Document -> comment rel")
    domMod.StartNodeCounting()
    doc = domMod.implementation.createDocument(None,None,None)
    com = doc.createComment("Foo")
    doc.appendChild(com)
    tester.compare(2,domMod.GetNodeCount())
    del doc
    del com
    gc.collect() #Force collection
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

def test_df_tree(tester,domMod):
    import sys, gc
    gc.collect()  #Force to clean everything up
    tester.startTest("Document Fragment Tree")
    doc = domMod.implementation.createDocument(None,None,None)
    domMod.StartNodeCounting()
    df = doc.createDocumentFragment()
    elem = doc.createElementNS(None,"Foo")
    elem2 = doc.createElementNS(None,"Foo2")
    df.appendChild(elem)
    df.appendChild(elem2)
    tester.compare(3,domMod.GetNodeCount())
    del elem
    del elem2
    del df
    gc.collect() #Force collection
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()


def test_attributes(tester,domMod):
    import sys, gc
    gc.collect()  #Force to clean everything up
    tester.startTest("Element with setAttributeNodeNS")
    doc = domMod.implementation.createDocument(None,None,None)
    domMod.StartNodeCounting()
    elem = doc.createElementNS(None,"Foo")
    attr = doc.createAttributeNS(None,"Foo")
    elem.setAttributeNodeNS(attr)
    tester.compare(2,domMod.GetNodeCount())
    del elem
    del attr
    gc.collect() #Force collection
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

    tester.startTest("Element with setAttributeNS")
    doc = domMod.implementation.createDocument(None,None,None)
    domMod.StartNodeCounting()
    elem = doc.createElementNS(None,"Foo")
    elem.setAttributeNS(None,"Foo","Bar")
    tester.compare(2,domMod.GetNodeCount())
    del elem
    gc.collect() #Force collection
    #tester.warning("This test fails in cDomlette")
    tester.compare(0,domMod.GetNodeCount())
    tester.testDone()

# -- cyclic garbage collection -----------------------------------------

def test_cycles(tester,domMod):
    tester.startGroup("Reclaiming of Cyclic Memory")
    test_empty_node(tester,domMod)
    test_small_tree(tester,domMod)
    test_df_tree(tester,domMod)
    test_attributes(tester,domMod)
    tester.groupDone()

# -- reference counts --------------------------------------------------

def test_refcounts(tester,domMod):
    tester.startGroup("Low Level Ref Counts")

    tester.startGroup("Internal Created Doc")
    domMod.TestRefCounts(tester,None)
    tester.groupDone()

    tester.startGroup("Empty Doc")
    doc = domMod.implementation.createDocument(None,None,None)
    domMod.TestRefCounts(tester,doc)
    del doc
    gc.collect() #Force collection
    tester.groupDone()

    tester.startGroup("Internal Created Dom")
    domMod.StartNodeCounting()
    dom = domMod.TestTree()
    domMod.TestRefCounts(tester,dom)
    del dom
    gc.collect() #Force collection
    tester.compare(0,domMod.GetNodeCount())
    tester.groupDone()

    tester.startGroup("Hand Created Dom")
    #Becareful to delete all external references exept to the doc
    domMod.StartNodeCounting()
    doc = domMod.implementation.createDocument(None,None,None)
    e = doc.createElementNS('http://foo.com','foo:root')
    doc.appendChild(e)
    
    t = doc.createTextNode("Data1")
    e.appendChild(t)
    del t

    p = doc.createProcessingInstruction("tar","Data3")
    doc.insertBefore(p,e)
    del p

    c = doc.createComment("Data2")
    doc.appendChild(c)
    del c

    e2 = doc.createElementNS('http://foo2.com','foo2:child')
    e.appendChild(e2)
    e2.setAttributeNS('http://foo2.com','foo2:attr','value')
    del e2

    del e
    domMod.TestRefCounts(tester,doc)
    del doc
    gc.collect() #Force collection
    tester.groupDone()

    import test_domlette_readers

    isrc = InputSource.DefaultFactory.fromString(test_domlette_readers.SMALL_XML,'mem')

    tester.startGroup("Small parsed XML")
    domMod.StartNodeCounting()
    dom = domMod.NonvalParse(isrc)
    domMod.TestRefCounts(tester,dom)
    del dom
    gc.collect() #Force collection
    tester.groupDone()

    isrc = InputSource.DefaultFactory.fromString(test_domlette_readers.LARGE_XML,'mem')

    tester.startGroup("Large parsed XML")
    domMod.StartNodeCounting()
    dom = domMod.NonvalParse(isrc)
    domMod.TestRefCounts(tester,dom)
    del dom
    gc.collect() #Force collection
    tester.groupDone()

    isrc = InputSource.DefaultFactory.fromString(test_domlette_readers.SMALL_XML,'mem')

    tester.startGroup("Small parsed XML w/ mod")
    domMod.StartNodeCounting()
    dom = domMod.NonvalParse(isrc)
    for ctr in range(1000):
        dom.documentElement.setAttributeNS('http://foo.com','bar','baz')
    gc.collect() #Force collection

    domMod.TestRefCounts(tester,dom)
    del dom
    gc.collect() #Force collection
    tester.groupDone()

    tester.groupDone()
    return

# -- testing entry function --------------------------------------------

def test_memory(tester, domMod):
    tester.startGroup("Memory")
    test_cycles(tester, domMod)
    #test_refcounts(tester, domMod)
    tester.groupDone()
    return

