import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IrrigationComponent } from './irrigation.component';

describe('IrrigationComponent', () => {
  let component: IrrigationComponent;
  let fixture: ComponentFixture<IrrigationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IrrigationComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(IrrigationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
