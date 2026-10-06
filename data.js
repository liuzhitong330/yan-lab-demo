(function () {
  'use strict';
  window.YAN_DATA_READY = Promise.all([
    fetch('data/primary-data.json').then(r => { if (!r.ok) throw Error('Primary data unavailable'); return r.json(); }),
    fetch('data/secondary-data.json').then(r => { if (!r.ok) throw Error('Movie data unavailable'); return r.json(); })
  ]).then(([primary, secondary]) => ({primary, secondary}));
})();
