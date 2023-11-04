import {
  Component,
  ElementRef,
  EventEmitter,
  Output,
  ViewChild,
} from '@angular/core';
import { Ingredient } from 'src/app/shared/ingredient.model';
import { ShoppingListService } from '../shopping-list.service';

@Component({
  selector: 'app-shopping-edit',
  templateUrl: './shopping-edit.component.html',
  styleUrls: ['./shopping-edit.component.css'],
})
export class ShoppingEditComponent {
  @ViewChild('nameInput') nameInputRef: ElementRef;
  @ViewChild('amountInput') amountInputRef: ElementRef;
  constructor(private shoppingListService: ShoppingListService) {}

  addIngredient() {
    const name = this.nameInputRef.nativeElement.value;
    const amount = this.amountInputRef.nativeElement.value;
    if (parseInt(amount) < 1) {
      alert('Please enter a valid amount!');
      return;
    }
    if (`${parseInt(amount)}` !== amount) {
      alert('Please enter a valid amount!');
      return;
    }
    this.shoppingListService.addIngredient(
      new Ingredient(name, parseInt(amount))
    );
  }
}
