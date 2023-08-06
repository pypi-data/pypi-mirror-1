from django.db import connection, transaction


class TransactionContext(object):
    """ A context that manages a database transaction.
    Example:

        with TransactionContext() as transaction:
            BLOCK

    if BLOCK raises an exception, the transaction is rolled back,
    but if everything falls through, the transaction is automatically
    commited at the end of BLOCK. """

    def __enter__(self):
        cursor = connection.cursor()
        transaction.enter_transaction_management()
        transaction.managed(True)
        return transaction

    def __exit__(self, e_type, e_value, e_trace):
        if e_type:
            transaction.rollback()
            transaction.leave_transaction_management()
            raise e_type(e_value)
        transaction.commit() 
        transaction.leave_transaction_management()
