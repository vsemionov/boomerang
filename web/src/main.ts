import {enableProdMode}         from '@angular/core';
import {platformBrowserDynamic} from '@angular/platform-browser-dynamic';

import {AppModule} from './app/app.module';


// Enable production mode unless running locally
if (!/^localhost(:\d+)?$/.test(document.location.host) && !/^127\.0\.0\.1(:\d+)?$/.test(document.location.host)) {
    enableProdMode();
}

platformBrowserDynamic().bootstrapModule(AppModule);
