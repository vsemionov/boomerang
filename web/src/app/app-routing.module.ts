import {NgModule}             from '@angular/core';
import {RouterModule, Routes} from '@angular/router';

import {NotebooksComponent} from './notebooks.component';
import {TasksComponent}     from './tasks.component';


const routes: Routes = [
    {path: 'notebooks', component: NotebooksComponent},
    {path: 'tasks', component: TasksComponent},
];


@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule {
}
