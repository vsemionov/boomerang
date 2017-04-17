import {Component} from '@angular/core';

@Component({
    selector: 'app',
    template: `<h1>Boomerang {{version}}</h1>`,
})
export class AppComponent {
    version = '0.6-dev';
}
