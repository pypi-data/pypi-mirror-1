"""Isolation Level definitions for Dejavu

We follow the terminology of ANSI for specifying isolation levels,
but you should be aware that:

 1. The four isolation levels defined therein do not begin to cover
    all the differences between competing transaction schemes, and
 
 2. Different products and discussions use terms differently.

In particular, http://citeseer.ist.psu.edu/berenson95critique.html
shows that the ANSI definitions are themselves subject to a range
of interpretations, so that even "sticking to the standard" is
open to misunderstanding. For safety reasons, we use the "broad"
interpretations (as defined by berenson95), so that each isolation
level not only prevents the corresponding phenomena, but prevents
situations which MIGHT lead to the phenomena. For example, when
we say that the "Read Committed" level prevents the "Dirty Read"
phenomenon, we mean that we forbid both the "strict" interpretation:

      Transaction 1       Transaction 2
         write x
                             read x
          abort              commit

and ALSO the "broad" interpretation:

      Transaction 1       Transaction 2
         write x
                             read x
       commit/abort       commit/abort

Now, "forbid" is unfortunately also open to interpretation. Different
stores (databases) will exhibit different behavior for different
phenomena. For the above example, PostgreSQL prohibits dirty reads
(for the appropriate levels) by returning the unaltered data to
Transaction 2. MySQL returns unaltered data for all levels except
SERIALIZABLE, for which it raises a lock timeout. Microsoft SQL Server
raises a CommandTimeout for READ COMMITTED and above.

Note also that MVCC architectures parallel single-version locking
schemes in ways that are difficult to equate and map perfectly.
Postgres, for example, allows you to declare all four ANSI levels,
but internally only uses two of them due to its MVCC architecture.

Finally, note that each Storage Manager allows you to directly
set the values for the isolation levels which are sent to your
back end (usually via a separate configuration option).
These names are merely a convenience feature to provide a
common map, so that mixing and migration of stores is easier.
"""

anomalies = [
    #       Transaction 1       Transaction 2
    #          write x
    #                              write x
    #        commit/abort       commit/abort
    "Dirty Write",
    
    #       Transaction 1       Transaction 2
    #          write x
    #                              read x
    #        commit/abort       commit/abort
    "Dirty Read",
    
    #       Transaction 1       Transaction 2
    #          read x
    #                              write x
    #          write x
    #           commit
    "Lost Update",
    
    #       Transaction 1       Transaction 2
    #          read x (cursor)
    #                              write x
    #          write x
    #           commit
    "Cursor Lost Update",
    
    #       Transaction 1       Transaction 2
    #           read x
    #                              write x
    #        commit/abort       commit/abort
    "Nonrepeatable Read",
    
    # Where x and y have consistency constraints:
    #       Transaction 1       Transaction 2
    #           read x
    #                              write x
    #                              write y
    #                              commit
    #           read y
    #        commit/abort
    "Read Skew",
    
    # Where x and y have consistency constraints:
    #       Transaction 1       Transaction 2
    #           read x
    #                              read y
    #           write y
    #                              write x
    #           commit             commit
    "Write Skew",
    
    #       Transaction 1       Transaction 2
    #           read P
    #                           write y in P
    #        commit/abort       commit/abort
    "Phantom",
    ]


class IsolationLevel(object):
    
    def __init__(self, name, forbidden):
        self.name = name
        self.forbidden = forbidden
    
    def forbids(self, anomaly):
        return (anomaly in self.forbidden)
    
    def __repr__(self):
        return "IsolationLevel(%r)" % self.name


DEGREE_0 = IsolationLevel("DEGREE 0", [])
READ_UNCOMMITTED = IsolationLevel("READ UNCOMMITTED",
                                  ["Dirty Write"])
READ_COMMITTED = IsolationLevel("READ COMMITTED",
                                ["Dirty Write", "Dirty Read"])
CURSOR_STABILITY = IsolationLevel("CURSOR STABILITY",
                                ["Dirty Write", "Dirty Read",
                                 "Cursor Lost Update"])
SNAPSHOT = IsolationLevel("SNAPSHOT",
                          ["Dirty Write", "Dirty Read",
                           "Cursor Lost Update", "Lost Update",
                           "Nonrepeatable Read", "Read Skew"])
REPEATABLE_READ = IsolationLevel("REPEATABLE READ",
                                ["Dirty Write", "Dirty Read",
                                 "Cursor Lost Update", "Lost Update",
                                 "Nonrepeatable Read", "Read Skew", "Write Skew"])
SERIALIZABLE = IsolationLevel("SERIALIZABLE",
                              ["Dirty Write", "Dirty Read",
                               "Cursor Lost Update", "Lost Update",
                               "Nonrepeatable Read", "Phantom",
                               "Read Skew", "Write Skew"])

levels = [DEGREE_0, READ_UNCOMMITTED, READ_COMMITTED, CURSOR_STABILITY,
          SNAPSHOT, REPEATABLE_READ, SERIALIZABLE]
