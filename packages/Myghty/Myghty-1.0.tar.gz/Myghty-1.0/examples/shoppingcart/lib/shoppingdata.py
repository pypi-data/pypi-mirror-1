from shoppingmodel import *


store = Category('store', 'The Myghty Store', [])

    
tshirts = Category("tshirts", "T Shirts",
    [
        Item("Myghty T Shirt", "A lovely T-shirt made with genuine Microsoft Paint, featuring the Myghty logo", "tshirt_myghty.gif", None, variants =
            [
                Variant('size', 'small', 9.99),
                Variant('size', 'medium', 10.99),
                Variant('size', 'large', 11.99),
                Variant('size', 'xtra large', 12.99),
                Variant('color', 'white'),
                Variant('color', 'black'),
                Variant('color', 'blue')
            ]
        ),
        
        Item("Python T Shirt", "A lovely T-shirt, carefully line drawn in less than five minutes, featuring the Python logo", "tshirt_python.gif", 10.99, variants = 
            [
                Variant('size', 'small'),
                Variant('size', 'medium'),
                Variant('size', 'large'),
                Variant('size', 'xtra large'),
            ]
        ),
        Item("Snake T Shirt", "Our finest shirt, features more pixels and colors than our other shirts.", "tshirt_snake.gif", 10.99, variants = 
            [
                Variant('size', 'small'),
                Variant('size', 'medium'),
                Variant('size', 'large'),
                Variant('size', 'xtra large'),
            ]
        )
    ],
    store)
    
mugs = Category("mugs", "Mugs",
    [
        Item("Myghty Mug", "Get your caffeine on with this mediocre line drawing", "mug_myghty.gif", 5.99),
        Item("Python Mug", "Get your caffeine on with this mediocre line drawing", "mug_python.gif", 5.99, 
                [
                Variant('color', 'white'),
                Variant('color', 'black'),
                Variant('color', 'blue')
                ]
        ),
        Item("Snake Mug", "Get your caffeine on with this mediocre line drawing", "mug_snake.gif", 5.99),
    ],
    store)
    

hats = Category("hats", "Hats",
    [
        Item("Myghty Hat", "This hat I could barely even draw, but you'll look cool.", "hat_myghty.gif", 8.99,
            [
                Variant('size', 'small'),
                Variant('size', 'medium'),
                Variant('size', 'large'),
            ]),
        Item("Python Hat", "This hat I could barely even draw, but you'll look cool.", "hat_python.gif", 6.75),
        Item("Snake Hat", "This hat I could barely even draw, but you'll look cool.", "hat_snake.gif", 6.75),
    ],
    store)


featureditems = Category("featureditems", "Featured Items", [
        hats.items[2],
        mugs.items[1],
        tshirts.items[0]
    ],
    None)
    
