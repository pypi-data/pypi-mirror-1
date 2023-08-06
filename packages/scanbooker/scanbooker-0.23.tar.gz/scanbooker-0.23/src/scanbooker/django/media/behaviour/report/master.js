// report/master.js - report behaviour control

var scanBookerReport;

window.addEvent('load', function () {
    scanBookerReport = new Report({})
    startup.bind(scanBookerReport)();

});

var startup = function () {
    this.addRpcService({
       smdUrl: reportSmdPath,
       onComplete: initReport.bind(this)
    });
};

var initReport = function () {
    this.initReport(reportId);
};

