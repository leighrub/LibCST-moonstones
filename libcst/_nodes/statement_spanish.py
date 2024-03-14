# Copyright (c) Meta Platforms, Inc. and affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from dataclasses import dataclass
import re
from typing import Optional, Pattern, Union

from libcst._add_slots import add_slots
from libcst._maybe_sentinel import MaybeSentinel
from libcst._nodes.base import CSTValidationError
from libcst._nodes.expression import BaseExpression
from libcst._nodes.expression import ExpressionPosition
from libcst._nodes.expression import From
from libcst._nodes.internal import CodegenState
from libcst._nodes.internal import visit_optional
from libcst._nodes.internal import visit_sentinel
from libcst._nodes.internal import visit_sentinel
from libcst._nodes.op import Semicolon
from libcst._nodes.statement import BaseSmallStatement
from libcst._nodes.whitespace import SimpleWhitespace
from libcst._visitors import CSTVisitorT


_INDENT_WHITESPACE_RE: Pattern[str] = re.compile(r"[ \f\t]+", re.UNICODE)

# Raise


@add_slots
@dataclass(frozen=True)
class Aumenta(BaseSmallStatement):
  """A ``aumenta exc`` or ``aumenta exc from cause`` statement."""

  #: The exception that we should aumenta.
  exc: Optional[BaseExpression] = None

  #: Optionally, a ``from cause`` clause to allow us to aumenta an exception
  #: out of another exception's context.
  cause: Optional[From] = None

  #: Any whitespace appearing between the ``aumenta`` keyword and the exception.
  whitespace_after_aumenta: Union[SimpleWhitespace, MaybeSentinel] = (
      MaybeSentinel.DEFAULT
  )

  #: Optional semicolon when this is used in a statement line. This semicolon
  #: owns the whitespace on both sides of it when it is used.
  semicolon: Union[Semicolon, MaybeSentinel] = MaybeSentinel.DEFAULT

  def _validate(self) -> None:
    # Validate correct construction
    if self.exc is None and self.cause is not None:
      raise CSTValidationError(
          "Must have an 'exc' when specifying 'clause'. on Aumenta."
      )

    # Validate spacing between "aumenta" and "exc"
    exc = self.exc
    if exc is not None:
      whitespace_after_aumenta = self.whitespace_after_aumenta
      has_no_gap = (
          not isinstance(whitespace_after_aumenta, MaybeSentinel)
          and whitespace_after_aumenta.empty
      )
      if has_no_gap and not exc._safe_to_use_with_word_operator(
          ExpressionPosition.RIGHT
      ):
        raise CSTValidationError(
            "Must have at least one space after 'aumenta'."
        )

    # Validate spacing between "exc" and "from"
    cause = self.cause
    if exc is not None and cause is not None:
      whitespace_before_from = cause.whitespace_before_from
      has_no_gap = (
          not isinstance(whitespace_before_from, MaybeSentinel)
          and whitespace_before_from.empty
      )
      if has_no_gap and not exc._safe_to_use_with_word_operator(
          ExpressionPosition.LEFT
      ):
        raise CSTValidationError("Must have at least one space before 'from'.")

  def _visit_and_replace_children(self, visitor: CSTVisitorT) -> "Aumenta":
    return Aumenta(
        whitespace_after_aumenta=visit_sentinel(
            self,
            "whitespace_after_aumenta",
            self.whitespace_after_aumenta,
            visitor,
        ),
        exc=visit_optional(self, "exc", self.exc, visitor),
        cause=visit_optional(self, "cause", self.cause, visitor),
        semicolon=visit_sentinel(self, "semicolon", self.semicolon, visitor),
    )

  def _codegen_impl(
      self, state: CodegenState, default_semicolon: bool = False
  ) -> None:
    with state.record_syntactic_position(self):
      exc = self.exc
      cause = self.cause
      state.add_token("aumenta")
      whitespace_after_aumenta = self.whitespace_after_aumenta
      if isinstance(whitespace_after_aumenta, MaybeSentinel):
        if exc is not None:
          state.add_token(" ")
      else:
        whitespace_after_aumenta._codegen(state)
      if exc is not None:
        exc._codegen(state)
      if cause is not None:
        cause._codegen(state, default_space=" ")

    semicolon = self.semicolon
    if isinstance(semicolon, MaybeSentinel):
      if default_semicolon:
        state.add_token("; ")
    elif isinstance(semicolon, Semicolon):
      semicolon._codegen(state)


# Continue
@add_slots
@dataclass(frozen=True)
class Continúa(BaseSmallStatement):
  """Represents a ``continúa`` statement, which is used to skip to the next iteration

  in a :class:`For` or :class:`While` loop.
  """

  #: Optional semicolon when this is used in a statement line. This semicolon
  #: owns the whitespace on both sides of it when it is used.
  semicolon: Union[Semicolon, MaybeSentinel] = MaybeSentinel.DEFAULT

  def _visit_and_replace_children(self, visitor: CSTVisitorT) -> "Continúa":
    return Continúa(
        semicolon=visit_sentinel(self, "semicolon", self.semicolon, visitor)
    )

  def _codegen_impl(
      self, state: CodegenState, default_semicolon: bool = False
  ) -> None:
    with state.record_syntactic_position(self):
      state.add_token("continúa")

    semicolon = self.semicolon
    if isinstance(semicolon, MaybeSentinel):
      if default_semicolon:
        state.add_token("; ")
    elif isinstance(semicolon, Semicolon):
      semicolon._codegen(state)


# Return


@add_slots
@dataclass(frozen=True)
class Devuelve(BaseSmallStatement):
  """Represents a ``devuelve`` or a ``devuelve x`` statement."""

  #: The optional expression that will be evaluated and returned.
  value: Optional[BaseExpression] = None

  #: Optional whitespace after the ``devuelve`` keyword before the optional
  #: value expression.
  whitespace_after_devuelve: Union[SimpleWhitespace, MaybeSentinel] = (
      MaybeSentinel.DEFAULT
  )

  #: Optional semicolon when this is used in a statement line. This semicolon
  #: owns the whitespace on both sides of it when it is used.
  semicolon: Union[Semicolon, MaybeSentinel] = MaybeSentinel.DEFAULT

  def _validate(self) -> None:
    value = self.value
    if value is not None:
      whitespace_after_devuelve = self.whitespace_after_devuelve
      has_no_gap = (
          not isinstance(whitespace_after_devuelve, MaybeSentinel)
          and whitespace_after_devuelve.empty
      )
      if has_no_gap and not value._safe_to_use_with_word_operator(
          ExpressionPosition.RIGHT
      ):
        raise CSTValidationError(
            "Must have at least one space after 'devuelve'."
        )

  def _visit_and_replace_children(self, visitor: CSTVisitorT) -> "Devuelve":
    return Devuelve(
        whitespace_after_devuelve=visit_sentinel(
            self,
            "whitespace_after_devuelve",
            self.whitespace_after_devuelve,
            visitor,
        ),
        value=visit_optional(self, "value", self.value, visitor),
        semicolon=visit_sentinel(self, "semicolon", self.semicolon, visitor),
    )

  def _codegen_impl(
      self, state: CodegenState, default_semicolon: bool = False
  ) -> None:
    with state.record_syntactic_position(self):
      state.add_token("devuelve")
      whitespace_after_devuelve = self.whitespace_after_devuelve
      value = self.value
      if isinstance(whitespace_after_devuelve, MaybeSentinel):
        if value is not None:
          state.add_token(" ")
      else:
        whitespace_after_devuelve._codegen(state)
      if value is not None:
        value._codegen(state)

    semicolon = self.semicolon
    if isinstance(semicolon, MaybeSentinel):
      if default_semicolon:
        state.add_token("; ")
    elif isinstance(semicolon, Semicolon):
      semicolon._codegen(state)


# Break
@add_slots
@dataclass(frozen=True)
class Rompe(BaseSmallStatement):
  """Represents a ``rompe`` statement, which is used to rompe out of a :class:`For`

  or :class:`While` loop early.
  """

  #: Optional semicolon when this is used in a statement line. This semicolon
  #: owns the whitespace on both sides of it when it is used.
  semicolon: Union[Semicolon, MaybeSentinel] = MaybeSentinel.DEFAULT

  def _visit_and_replace_children(self, visitor: CSTVisitorT) -> "Rompe":
    return Rompe(
        semicolon=visit_sentinel(self, "semicolon", self.semicolon, visitor)
    )

  def _codegen_impl(
      self, state: CodegenState, default_semicolon: bool = False
  ) -> None:
    with state.record_syntactic_position(self):
      state.add_token("rompe")

    semicolon = self.semicolon
    if isinstance(semicolon, MaybeSentinel):
      if default_semicolon:
        state.add_token("; ")
    elif isinstance(semicolon, Semicolon):
      semicolon._codegen(state)
