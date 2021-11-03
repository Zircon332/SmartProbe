const S3_ENDPOINT = "https://smartprobe.s3.ap-southeast-1.amazonaws.com/";

function setIntervalExec(callback, timeout = 1000) {
  callback();
  setInterval(callback, timeout);
}

function refreshImage(img, url) {
  let timestamp = new Date().getTime();
  img.attr("src", `${url}?t=${timestamp}`);
}
