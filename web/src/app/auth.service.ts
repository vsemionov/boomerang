import {Injectable} from '@angular/core';

import {AuthConfig}      from 'angular2-jwt';
import {JwtHelper}       from 'angular2-jwt';
import {tokenNotExpired} from 'angular2-jwt';
import {CookieService}   from 'angular2-cookie/services/cookies.service';


@Injectable()
export class AuthService {
    private jwtHelper: JwtHelper = new JwtHelper();

    static getAuthConfig() {
        return new AuthConfig({'headerPrefix': 'JWT'});
    }

    constructor(private cookieService: CookieService) {
    }

    init() {
        let token = this.cookieService.get('jwt');
        if (token) {
            this.login(token);
        }
        this.cookieService.remove('jwt');
    }

    login(token: string) {
        let username = this.jwtHelper.decodeToken(token).username;
        localStorage.setItem('username', username);
        localStorage.setItem('token', token);
    }

    logout() {
        localStorage.removeItem('username');
        localStorage.removeItem('token');
    }

    isLoggedIn() {
        return tokenNotExpired();
    }
}
