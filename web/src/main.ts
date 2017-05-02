import {enableProdMode}  from '@angular/core';
import {platformBrowser} from '@angular/platform-browser';

import {AppModuleNgFactory} from '../aot/web/src/app/app.module.ngfactory';


// Enable production mode unless running locally
if (!/^localhost(:\d+)?$/.test(document.location.host) && !/^127\.0\.0\.1(:\d+)?$/.test(document.location.host)) {
    enableProdMode();
}

platformBrowser().bootstrapModuleFactory(AppModuleNgFactory);
