import { Component, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css'],
})
export class HeaderComponent {
  @Output() featureSelected = new EventEmitter<HeaderName>();
  collapsed = true;

  onSelect(headerName: HeaderName) {
    this.featureSelected.emit(headerName);
  }
}

type HeaderName = 'recipes' | 'shoppingList';
