import {Component, OnInit} from '@angular/core';
import {Router}            from '@angular/router';

@Component({
    selector: 'app',
    template: `
        <h1>Boomerang {{version}}</h1>
        <div>
            <a routerLink="/notebooks" routerLinkActive="active">Notebooks</a>
        </div>
        <div>
            <a routerLink="/tasks" routerLinkActive="active">Tasks</a>
        </div>
        <div>
            <router-outlet></router-outlet>
        </div>
    `,
})
export class AppComponent implements OnInit {
    constructor(private router: Router) {
    }

    ngOnInit(): void {
        this.router.navigate(['/notebooks']);
    }
}
