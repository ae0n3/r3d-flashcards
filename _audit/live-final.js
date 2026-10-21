const CDP_PORT = process.argv[2];
const URL = process.argv[3];
const { CDP } = require(' CDP');
const cdp = new CDP({ port: CDP_PORT });
cdp.on('Page.frameStoppedLoading', (event) => {
  console.log('frame:', event.frame.url);
});
cdp.on('Runtime.consoleAPICalled', (event) => {
  console.log('console:', event.message.text);
});
cdp.send('Page.enable');
cdp.send('Page.navigate', { url: URL });
cdp.send('Runtime.enable');
// wait for load
setTimeout(() => {
  cdp.send('Runtime.evaluate', { expression: 'document.querySelectorAll(\'a[href*="lesson"]').length', returnByValue: true }, (res) => {
    console.log('lesson links:', res.result.value);
  });
  cdp.send('Runtime.evaluate', { expression: 'window.R3D_DATA && window.R3D_DATA.cards && Object.keys(window.R3D_DATA.cards).length', returnByValue: true }, (res) => {
    console.log('card groups:', res.result.value);
  });
  cdp.send('Page.stopLoading');
  setTimeout(() => cdp.disconnect(), 1000);
}, 3000);
