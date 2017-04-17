import {NgModule}             from '@angular/core';
import {BrowserModule}        from '@angular/platform-browser';
import {Http, RequestOptions} from '@angular/http';

import {AuthHttp}      from 'angular2-jwt';
import {CookieService} from 'angular2-cookie/services/cookies.service';

import {AppRoutingModule} from './app-routing.module';

import {AuthService} from './auth.service';

import {AppComponent}         from './app.component';
import {NavbarComponent}      from './navbar.component';
import {BreadcrumbsComponent} from './breadcrumbs.component';
import {NotebooksComponent}   from './notebooks.component';
import {TasksComponent}       from './tasks.component';


export function authHttpServiceFactory(http: Http, options: RequestOptions) {
    return new AuthHttp(AuthService.getAuthConfig(), http, options);
}


@NgModule({
    imports: [
        BrowserModule,
        AppRoutingModule,
    ],
    declarations: [
        AppComponent,
        NavbarComponent,
        BreadcrumbsComponent,
        NotebooksComponent,
        TasksComponent,
    ],
    providers: [
        {
            provide: AuthHttp,
            useFactory: authHttpServiceFactory,
            deps: [Http, RequestOptions]
        },
        CookieService,
        AuthService
    ],
    bootstrap: [AppComponent]
})
export class AppModule {
}
