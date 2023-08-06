






#######################################################################
# def sum_covers(expr1, expr2, subst):
#     vrs = filter(expr1.args, lambda x: x.var)
#     nvrs = filter(expr1.args, lambda x: not x.var)
#     ret = {}
#     if vrs:
#         if nvrs:
#             expr = nvrs[0]
#             if expr.arith == 2:
#
#             elif expr.arith == 1:
#                 res = str(int(expr.symbol) - int(expr2.symbol))
#                 if subst.has_key(vrs[0].symbol):
#                     if res != subst[vrs[0].symbol]:
#                         return False
#                 else:
#                     ret[vrs[0].symbol] = res
#         else:
#             ret[vrs[0].symbol] = 'dif(%s, %s)' % (expr2.symbol,
#                                                         vrs[1].symbol)
#             ret[vrs[1].symbol] = 'dif(%s, %s)' % (expr2.symbol,
#                                                         vrs[0].symbol)
#     else:
#         nums = filter(nvrs, lambda x: not x.var)
#         funs = nvrs - nums
#         sum_covers(nvrs[
#
#     return ret