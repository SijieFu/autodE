# from autode import methods


# def test_get_hmethod():
#     methods.Config.hcode = None
#     method1 = methods.get_hmethod()
#     assert type(method1) == type(methods.ORCA())

#     methods.Config.hcode = 'ORCA'
#     method2 = methods.get_hmethod()
#     assert type(method2) == type(methods.ORCA())


# def test_get_lmethod():
#     methods.Config.lcode = None
#     method3 = methods.get_lmethod()
#     assert type(method3) == type(methods.XTB())

#     methods.Config.lcode = 'XTB'
#     method4 = methods.get_lmethod()
#     assert type(method4) == type(methods.XTB())

#     methods.Config.lcode = 'MOPAC'
#     method4 = methods.get_lmethod()
#     assert type(method4) == type(methods.XTB())
