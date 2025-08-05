// Shared domain value objects
export abstract class ValueObject {
  abstract equals(other: ValueObject): boolean;
  abstract hashCode(): number;
}

export class Money extends ValueObject {
  constructor(
    public readonly amount: number,
    public readonly currency: string = 'EUR'
  ) {
    super();
    if (amount < 0) {
      throw new Error('Money amount cannot be negative');
    }
    if (!currency) {
      throw new Error('Currency cannot be empty');
    }
  }

  equals(other: ValueObject): boolean {
    if (!(other instanceof Money)) return false;
    return this.amount === other.amount && this.currency === other.currency;
  }

  hashCode(): number {
    return this.amount.toString().concat(this.currency).length;
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Cannot add money with different currencies');
    }
    return new Money(this.amount + other.amount, this.currency);
  }

  multiply(factor: number): Money {
    return new Money(this.amount * factor, this.currency);
  }

  format(): string {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: this.currency,
    }).format(this.amount);
  }
}

export class Email extends ValueObject {
  constructor(public readonly value: string) {
    super();
    if (!this.isValidEmail(value)) {
      throw new Error(`Invalid email format: ${value}`);
    }
  }

  equals(other: ValueObject): boolean {
    if (!(other instanceof Email)) return false;
    return this.value.toLowerCase() === other.value.toLowerCase();
  }

  hashCode(): number {
    return this.value.toLowerCase().length;
  }

  private isValidEmail(email: string): boolean {
    const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return pattern.test(email);
  }
}

export class UserId extends ValueObject {
  constructor(public readonly value: string) {
    super();
    if (!value || !value.trim()) {
      throw new Error('UserId cannot be empty');
    }
  }

  equals(other: ValueObject): boolean {
    if (!(other instanceof UserId)) return false;
    return this.value === other.value;
  }

  hashCode(): number {
    return this.value.length;
  }
}

export class PokemonId extends ValueObject {
  constructor(public readonly value: number) {
    super();
    if (value <= 0) {
      throw new Error('PokemonId must be positive');
    }
  }

  equals(other: ValueObject): boolean {
    if (!(other instanceof PokemonId)) return false;
    return this.value === other.value;
  }

  hashCode(): number {
    return this.value;
  }
}

export class CartId extends ValueObject {
  constructor(public readonly value: string) {
    super();
    if (!value || !value.trim()) {
      throw new Error('CartId cannot be empty');
    }
  }

  equals(other: ValueObject): boolean {
    if (!(other instanceof CartId)) return false;
    return this.value === other.value;
  }

  hashCode(): number {
    return this.value.length;
  }
}
