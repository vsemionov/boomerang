import {Component} from '@angular/core';

import {AuthService} from './auth.service';


@Component({
    selector: 'navbar',
    template: `
        <div>navbar</div>
        <div *ngIf="authService.isLoggedIn()">logged in</div>
    `,
})
export class NavbarComponent {
    constructor(private authService: AuthService) {
    }
}
