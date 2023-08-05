def Test(tester):

    tester.startGroup('Boolean Expressions')

    tester.startTest('Creating test environment')
    from Ft.Xml.XPath import ParsedExpr
    from Ft.Lib import boolean

    from DummyExpr import boolT, boolF
    from DummyExpr import num3, numN4, num4p5, numNan, numInf
    from DummyExpr import strPi, strText, STR_EGG1, STR_EGG2
    from DummyExpr import EMPTY_NODE_SET, ONE_NODE_SET, TWO_NODE_SET
    
    tests = {ParsedExpr.ParsedRelationalExpr : [((0, strPi, numN4), boolean.false),
                                                ((1, strPi, numN4), boolean.false),
                                                ((2, strPi, numN4), boolean.true),
                                                ((3, strPi, strPi), boolean.true),
                                                ((0, numNan, numN4), boolean.false),
                                                ((1, numNan, numN4), boolean.false),
                                                ((2, numNan, numN4), boolean.false),
                                                ((3, numNan, strPi), boolean.false),
                                                ],
             ParsedExpr.ParsedEqualityExpr : [(('=', strPi, strPi), boolean.true),
                                              (('=', strPi, strText), boolean.false),
                                              (('!=', strPi, numN4), boolean.true),
                                              (('=', numNan, strText), boolean.false),
                                              (('!=', numNan, numN4), boolean.true),
                                              (('=', numNan, numNan), boolean.false),
                                              (('!=', numNan, numNan), boolean.true),
                                              (('=', EMPTY_NODE_SET, boolT), boolean.false),
                                              (('!=', EMPTY_NODE_SET, boolT), boolean.false),
                                              (('=', EMPTY_NODE_SET, boolF), boolean.false),
                                              (('!=', EMPTY_NODE_SET, boolF), boolean.false),
                                              (('=', EMPTY_NODE_SET, ONE_NODE_SET), boolean.false),
                                              (('!=', EMPTY_NODE_SET, ONE_NODE_SET), boolean.false),
                                              (('=', ONE_NODE_SET, EMPTY_NODE_SET), boolean.false),
                                              (('!=', ONE_NODE_SET, EMPTY_NODE_SET), boolean.false),
                                              (('=', ONE_NODE_SET, ONE_NODE_SET), boolean.true),
                                              (('!=', ONE_NODE_SET, ONE_NODE_SET), boolean.false),
                                              (('=', STR_EGG1, ONE_NODE_SET), boolean.true),
                                              (('!=', STR_EGG1, ONE_NODE_SET), boolean.false),
                                              (('=', STR_EGG2, ONE_NODE_SET), boolean.false),
                                              (('!=', STR_EGG2, ONE_NODE_SET), boolean.true),
                                              (('=', STR_EGG1, TWO_NODE_SET), boolean.true),
                                              (('!=', STR_EGG1, TWO_NODE_SET), boolean.true), #Yeah, non-intuitive, but boolean.true acc to XPath spec 3.4
                                              ],
             ParsedExpr.ParsedAndExpr : [((boolT, boolT), boolean.true),
                                         ((boolT, boolF), boolean.false),
                                         ((boolF, boolF), boolean.false),
                                         ],
             ParsedExpr.ParsedOrExpr : [((boolT, boolF), boolean.true),
                                        ((boolT, boolT), boolean.true),
                                        ((boolF, boolF), boolean.false),
                                        ]
             }
    
    tester.testDone()

    for (expr, boolTests) in tests.items():
        for (args, expected) in boolTests:
            p = apply(expr, args)
            tester.startTest('Comparing %s' % repr(p))
            result = p.evaluate(None)
            tester.compare(result, expected)
            tester.testDone()

    tester.groupDone()
