
def log_centralise(file_mode, file_name,format_log):
    import logging
    logging.basicConfig(filename=file_name,
                        filemode=file_mode,
                        format=format_log,
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG
                        )