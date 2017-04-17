import {NgModule}      from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';
import {FormsModule}   from '@angular/forms';

import {AppRoutingModule} from './app-routing.module';

import {AuthService} from './auth.service';

import {AppComponent}         from './app.component';
import {NavbarComponent}      from './navbar.component';
import {BreadcrumbsComponent} from './breadcrumbs.component';
import {NotebooksComponent}   from './notebooks.component';
import {TasksComponent}       from './tasks.component';


@NgModule({
    imports: [
        BrowserModule,
        FormsModule,
        AppRoutingModule,
    ],
    declarations: [
        AppComponent,
        NavbarComponent,
        BreadcrumbsComponent,
        NotebooksComponent,
        TasksComponent,
    ],
    providers: [AuthService],
    bootstrap: [AppComponent]
})
export class AppModule {
}
