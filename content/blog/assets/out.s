  .file "test.c"
  .version	"01.01"
gcc2_compiled.:
.text
	.align 4
.globl add_i32
	.type	add_i32,@function
add_i32:
	pushl %ebp
	movl %esp,%ebp
	pushl %edi
	pushl %esi
	pushl %ebx
	movl 8(%ebp),%esi
	movl 12(%ebp),%ebx
	movl 16(%ebp),%ecx
	movl 20(%ebp),%edx
	xorl %eax,%eax
	cmpl %edx,%eax
	jge .L3
	.align 4
.L5
	movl (%ebx,%eax,4),%edi
	addl (%ecx,%eax,4),%edi
	movl %edi, (%esi,%eax,4)
	incl %eax
	cmpl %edx,%eax
	jl .L5
.L3
	leal -12(%ebp),%esp
	popl %ebx
	popl %esi
	popl %edi
	leave
	ret
.Lfe1
	.size	add_i32.Lfe1-add_i32
	.ident	"GCC: (GNU) 2.7.2.3"

