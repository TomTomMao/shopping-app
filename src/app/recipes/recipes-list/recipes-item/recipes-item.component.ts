import { Component, Input, Output, EventEmitter } from '@angular/core';
import { RecipeService } from '../../recipe.service';
import { Ingredient } from 'src/app/shared/ingredient.model';

@Component({
  selector: 'app-recipes-item',
  templateUrl: './recipes-item.component.html',
  styleUrls: ['./recipes-item.component.css'],
})
export class RecipesItemComponent {
  @Input() recipe: {
    name: string;
    description: string;
    imagePath: string;
    ingredients: Ingredient[];
  };

  // inject Recipeservice
  constructor(private recipeService: RecipeService) {}

  onSelectRecipe() {
    this.recipeService.recipeSelected.emit(this.recipe);
  }
}
