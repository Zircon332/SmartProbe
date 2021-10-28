function setIntervalExec(callback, timeout) {
  callback();
  setInterval(callback, timeout);
}
