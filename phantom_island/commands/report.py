"""The expedition's report: answering the task's questions, and the epilogue."""

from world.report import report

from .command import Command


class CmdReport(Command):
    """
    Write the expedition's report for the Society: answer the task's questions.

    Usage:
      report
      report <letter>
      report <number>
      report more

    The questions stand at the top of the journal. report shows the next open
    question and its choices. Pick the answer you can prove with its letter
    (report b). report 2 goes to the second question; they can be answered in
    any order, anywhere, and one answer counts for the whole expedition.

    A choice that doesn't fit is turned down, with a hint of where to look. Once
    every question is answered, the epilogue tells the whole story: report more
    turns its pages.

    Examples:
      report
      report 2
      report c
    """

    key = "report"
    locks = "cmd:all()"
    help_category = "General"

    def func(self) -> None:
        report(self.caller, self.args)
