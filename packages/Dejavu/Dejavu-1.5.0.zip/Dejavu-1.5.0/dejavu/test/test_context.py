"""Test for sandbox-as-context-manager in Python 2.5+."""

from __future__ import with_statement

import datetime
import dejavu


def test_with_context(arena):
    Zoo = arena.class_by_name('Zoo')
    
    def commit_test():
        """Test transaction commit."""
        with arena.new_sandbox() as box:
            WAP = box.unit(Zoo, Name='Wild Animal Park')
            WAP.Opens = now
    
    def rollback_test():
        """Test transaction rollback on error."""
        with arena.new_sandbox() as box:
            SDZ = box.unit(Zoo, Name='San Diego Zoo')
            SDZ.Name = 'The One and Only San Diego Zoo'
            SDZ.Founded = datetime.date(2039, 9, 13)
            a = 3/0
    
    now = datetime.time(5, 38, 24)
    commit_test()
    WAP = arena.new_sandbox().unit(Zoo, Name='Wild Animal Park')
    assert WAP.Opens == now
    
    try:
        rollback_test()
    except ZeroDivisionError:
        pass
    else:
        raise AssertionError("ZeroDivisionError not raised.")
    SDZ = arena.new_sandbox().unit(Zoo, Name='San Diego Zoo')
    assert SDZ.Name == 'San Diego Zoo'
    assert SDZ.Founded == datetime.date(1835, 9, 13)

