import { Component, OnInit } from '@angular/core';
import { ApiService } from '../../api.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-irrigation',
  standalone: true,
  templateUrl: './irrigation.component.html',
  styleUrls: ['./irrigation.component.css'],
  imports: [CommonModule],
})
export class IrrigationComponent implements OnInit {
  predictions: any[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit(): void {
    this.apiService.getIrrigation().subscribe({
      next: (res) => {
        if (res.status === 'success') {
          this.predictions = res.predictions;
        }
      },
      error: (err) => {
        console.error('Tahmin verisi alınamadı:', err);
      }
    });
  }
}
