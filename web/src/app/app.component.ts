import {Component, OnInit} from '@angular/core';
import {Router}            from '@angular/router';

import {AuthService} from './auth.service';


@Component({
    selector: 'app',
    template: `
        <h1>Boomerang {{version}}</h1>
        <navbar></navbar>
        <breadcrumbs></breadcrumbs>
        <hr/>
        <div>
            <a routerLink="/notebooks" routerLinkActive="btn">Notebooks</a>
        </div>
        <div>
            <a routerLink="/tasks" routerLinkActive="btn">Tasks</a>
        </div>
        <hr/>
        <router-outlet></router-outlet>
    `,
})
export class AppComponent implements OnInit {
    version = '0.6-dev';

    constructor(private router: Router, private authService: AuthService) {
    }

    ngOnInit() {
        this.authService.init();
        // this.router.navigate(['/notebooks']);
    }
}
