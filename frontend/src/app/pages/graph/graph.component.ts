import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-graph',
  standalone: true,
  templateUrl: './graph.component.html',
  styleUrls: ['./graph.component.css'],
  imports: [CommonModule],
})
export class GraphComponent implements OnInit {
  soilGraphUrl: string = '';
  temperatureGraphUrl: string = '';
  humidityGraphUrl: string = '';
  lightGraphUrl: string = ''; // Yeni eklendi
  modalImage: string | null = null;

  openImage(imageUrl: string) {
    this.modalImage = imageUrl;
  }
  
  closeImage() {
    this.modalImage = null;
  }
  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.apiService.getAllGraphs().subscribe({
      next: (response) => {
        console.log('Gelen Grafik JSON:', response); // Konsola yazdır
        this.soilGraphUrl = response['Toprak Nemi'];
        this.temperatureGraphUrl = response['Hava Sıcaklığı'];
        this.humidityGraphUrl = response['Hava Nemi'];
        this.lightGraphUrl = response['Işık Yoğunluğu'];
      },
      error: (err) => console.error('API Hatası:', err)
    });
  }
  
}