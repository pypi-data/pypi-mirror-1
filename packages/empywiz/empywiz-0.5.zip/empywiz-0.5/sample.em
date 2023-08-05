@%prompt 'askonce','once'
@%prompt 'number',"IntPrompter()"
@%prompt 'somearray',"ListPrompter()"
 --
Hello @askonce

Today you told me number @number, which is bigger than @(number-1)

The list of array elements:

@[for elem in somearray]
Array has, at least, the element @(elem)
@[end for]

 --