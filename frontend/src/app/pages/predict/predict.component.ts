import { Component } from '@angular/core';
import { ApiService } from '../../api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-predict',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './predict.component.html',
  styleUrl: './predict.component.css'
})
export class PredictComponent {
  inputData = {
    "ToprakNemi(%)": null,
    "HavaSicakligi(°C)": null,
    "HavaNemi(%)": null,
    "IsikYogunlugu(lux)": null
  };

  predictedLitre: number | null = null;
  errorMessage: string | null = null;

  constructor(private apiService: ApiService) {}

  onSubmit() {
    this.apiService.getPredictLiter(this.inputData).subscribe({
      next: (res) => {
        this.predictedLitre = res["TahminiSuMiktari(Litre)"];
        this.errorMessage = null;
      },
      error: (err) => {
        this.predictedLitre = null;
        this.errorMessage = err.error.message || "Sunucu hatası.";
      }
    });
  }
}
