# 15-Pixel LED Display Controller with Finite State Machine
[The project can be simulated here](https://www.tinkercad.com/things/kFDdGqKnbat-5x3-display-and-sequence-generator?sharecode=WqqfOPZSOn_uz6iXAdQBumaqDsZAPenCJGjMhOgIZEY)

`optimize.py` is the script used to find the best possible combination of boolean expressions (lowest gate input cost) for each J and K input in the sequence generator part of the project by using a greedy algorithm. The lowest cost product-of-sums and sum-of-products expressions are shown for each flipflop input, and the lowest cost initial state is shown as well in the console. The corresponding JK flipflops truth table is then exported to an excel file.
