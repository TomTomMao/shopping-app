import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-recipes-item',
  templateUrl: './recipes-item.component.html',
  styleUrls: ['./recipes-item.component.css'],
})
export class RecipesItemComponent {
  @Input() recipe: { name: string; description: string; imagePath: string };

  @Output() recipeSelected = new EventEmitter<void>();

  onSelectRecipe() {
    this.recipeSelected.emit();
    console.log('recipeSelected')
  }
}
