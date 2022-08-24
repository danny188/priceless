class ProductURLError(Exception):
    """Exception to indicate any errors associated with a product url

    Type of errors can include:
        - url format/syntax
        - product shop not supported
        - error responses from product api endpoints
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
