import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { RouterOutlet } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://127.0.0.1:5000';

  constructor(private http: HttpClient) {}

  getData(): Observable<any> {
    return this.http.get(`${this.baseUrl}/data`);
  }

  getGraph(): Observable<Blob> {
    return this.http.get(`${this.baseUrl}/graph/soil-moisture`, { responseType: 'blob' });
  }

  getIrrigation(): Observable<any> {
    return this.http.get(`http://localhost:5000/thingspeak`);
  }
  getAllGraphs(): Observable<any> { // <-- Bu metodu ekledik
    return this.http.get(`${this.baseUrl}/graph/all`);
  }
  getPredictLiter(data: any): Observable<any> {
    return this.http.post<any>('http://localhost:5000/predict_litre', data);
}
}
