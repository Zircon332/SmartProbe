class ServiceNode {
  constructor() {}

  getNodesAsync(onSuccess, onError = (err) => {}) {
    $.ajax({
      url: "/api/node/",
      success: onSuccess,
      error: onError
    });
  }
}
