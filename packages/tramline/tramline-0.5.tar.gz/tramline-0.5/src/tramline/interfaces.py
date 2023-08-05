class IInputFilterProcessor:
    def pushInput(data, out):
        """Push block of inputted data into processor.

        Processor writes data to pass along on input stream to
        out, using .write().
        """

    def finalizeInput(out):
        """Notify processor that input data is now complete.

        Processor can still choose to write data to pass along input
        stream to out, using .write().
        """

    def commit():
        """Commit any action taken during the input phase.
        """

    def abort():
        """"Abort action taken in the input phase.
        """
                
class IOutputFilterProcessor:
    def pushOutput(data, out):
        """Push block of outputted data into processor.

        Processor writes data to pass along on output stream to
        out, using .write().
        """

    def finalizeOutput(self, out):
        """Notify processor that output data is now complete.

        Processor can still choose to write data to pass along output
        stream to out, using .write().
        """
