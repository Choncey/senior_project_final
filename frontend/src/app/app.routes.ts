import { Routes } from '@angular/router';
import { HomeComponent } from './pages/home/home.component';
import { DataComponent } from './pages/data/data.component';
import { GraphComponent } from './pages/graph/graph.component';
import { IrrigationComponent } from './pages/irrigation/irrigation.component';
import { PredictComponent } from './pages/predict/predict.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'data', component: DataComponent },
  { path: 'graph', component: GraphComponent },
  { path: 'irrigation', component: IrrigationComponent },
  { path: 'predict', component: PredictComponent },
];