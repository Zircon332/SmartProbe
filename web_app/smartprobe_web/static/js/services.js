class ServiceNode {
  constructor() {}

  getNodesAsync(onSuccess, onError = (err) => {}) {
    $.ajax({
      url: "/api/node/",
      success: onSuccess,
      error: onError
    });
  }

  getNodeAsync(nodeId, onSuccess, onError = (err) => {}) {
    $.ajax({
      url: `/api/node/${nodeId}`,
      success: onSuccess,
      error: onError
    });
  }

  getNodeDataAsync(nodeId, onSuccess, onError = (err) => {}) {
    $.ajax({
      url: `/api/node/${nodeId}/data`,
      success: onSuccess,
      error: onError
    });
  }

  getNodeActionsAsync(nodeId, onSuccess, onError = (err) => {}) {
    $.ajax({
      url: `/api/node/${nodeId}/actions`,
      success: onSuccess,
      error: onError
    });
  }
}
