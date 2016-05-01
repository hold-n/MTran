class Vector {
    x: number;
    y: number;

    constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
    }
}

function scalar(a: Vector, b: Vector): number { // TODO: make it a method
    return a.x*b.x + a.y*b.y;
}

let a: Vector = new Vector(3, 4);
let b: Vector = new Vector(1, 2);
let product: number = scalar(a, b);

if (product === 11) {
    console.log('Assertion successful');
} else {
    console.log('Assertion failed');
}
