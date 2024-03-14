import libcst as cst

# Example Spanish code
spanish_code = """
# Calcula el factorial de un número
i = 0
while i < 3:
  i += 1
  rompe
"""

english_code = """
# Calcula el factorial de un número
i = 0
while i < 3:
  i += 1
  break
  break;
  continue
  continue;
  raise Exception("New Exception")

return
return True
return False;
"""


class TranslateToSpanishTransformer(cst.CSTTransformer):

  def leave_Break(
      self, original_node: cst.Break, updated_node: cst.Break
  ) -> cst.Rompe:
    return cst.Rompe(original_node.semicolon)

  def leave_Continue(
      self, original_node: cst.Continue, updated_node: cst.Continue
  ) -> cst.Continúa:
    return cst.Continúa(original_node.semicolon)

  def leave_Raise(
      self, original_node: cst.Raise, updated_node: cst.Raise
  ) -> cst.Aumenta:
    return cst.Aumenta(
        original_node.exc,
        original_node.cause,
        original_node.whitespace_after_raise,
        original_node.semicolon,
    )

  def leave_Return(
      self, original_node: cst.Return, updated_node: cst.Return
  ) -> cst.Devuelve:
    return cst.Devuelve(
        original_node.value,
        original_node.whitespace_after_return,
        original_node.semicolon,
    )


module = cst.parse_module(english_code)
modified_code = module.visit(TranslateToSpanishTransformer())
print(modified_code.code)
