function setIntervalExec(callback, timeout = 1000) {
  callback();
  setInterval(callback, timeout);
}
