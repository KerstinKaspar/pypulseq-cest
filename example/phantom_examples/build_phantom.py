from phantom.phantom import phantom_b0_inhom, phantom_b1_inhom,  phantom_fractions, phantom_tissues, plot_phantom
import matplotlib.pyplot as plt

phantom_t = phantom_tissues()

phantom_f = phantom_fractions()

fig_t, [ax_t1, ax_t2, ax_f, ax_b0, ax_b1] = plt.subplots(1, 5)# , figsize=(12, 9))
t1 = ax_t1.imshow(phantom_t[0])
ax_t1.title.set_text('Phantom: T1 values')
#plt.show()

#fig_t2, ax_t2 = plt.subplots(figsize=(12, 9))
t2 = ax_t2.imshow(phantom_t[1])
ax_t2.title.set_text('Phantom: T2 values')
#plt.show()

#fig_f, ax_f = plt.subplots(figsize=(12, 9))
f = ax_f.imshow(phantom_f[0])
ax_f.title.set_text('Phantom: fractions')
# plt.colorbar(f)
# plt.show()
# plt.savefig('test_phantom.jpg')

phantom_b0 = phantom_b0_inhom()
#fig_b, [ax_b0, ax_b1] = plt.subplots(1, 2)
b0 = ax_b0.imshow(phantom_b0[0])
ax_b0.title.set_text('Phantom: B0 inhomogeneity')
# plt.colorbar(b0)
#plt.show()

phantom_b1 = phantom_b1_inhom()
b1 = ax_b1.imshow(phantom_b1[0])
ax_b1.title.set_text('Phantom: B1 inhomogeneity')
# plt.colorbar(b0)
plt.show()