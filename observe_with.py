def observe_with(observer, event_handler, pathnames, recursive):
    """
    Single observer thread with a scheduled path and event handler.
    :param observer:
        The observer thread.
    :param event_handler:
        Event handler which will be called in response to file system events.
    :param pathnames:
        A list of pathnames to monitor.
    :param recursive:
        ``True`` if recursive; ``False`` otherwise.
    """
    for pathname in set(pathnames):
        observer.schedule(event_handler, pathname, recursive)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
