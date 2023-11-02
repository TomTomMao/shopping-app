import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  loadedFeature: 'recipes' | 'shoppingList' = 'recipes';
  onNavigate(feature: 'recipes' | 'shoppingList') {
    this.loadedFeature = feature;
  console.log(this.loadedFeature);
  }
}
