import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-data',
  standalone: true,
  templateUrl: './data.component.html',
  styleUrls: ['./data.component.css'],
  imports: [CommonModule],
})
export class DataComponent implements OnInit {
  dataset: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.apiService.getData().subscribe({
      next: (res) => {
        this.dataset = res;
        console.log('Veri geldi:', this.dataset);
      },
      error: (err) => console.error('Veri alınamadı:', err)
    });
  }
  getColor(renk: string): string {
    switch (renk?.toLowerCase()) {
      case 'yeşil':
      case 'yesil':
        return '#27ae60'; // yeşil
      case 'sarı':
      case 'sari':
        return '#f1c40f'; // sarı
      case 'kahverengi':
        return '#8b4513'; // kahverengi
      case 'kırmızı':
      case 'kirmizi':
        return '#e74c3c'; // kırmızı
      case 'mor':
        return '#9b59b6'; // mor
      default:
        return '#bdc3c7'; // gri (bilinmeyen)
    }
  }
}
