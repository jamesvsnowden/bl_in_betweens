# In-Betweens

In-between shape keys are intermediate shapes that modify other shape keys.
As a *hero* shape key value changes (normally from 0-1) one or more *in-between*
shape keys are interpolated with the *hero* shape key to control the deformation.
In-betweens allow considerably more precise control over deformation and are
particularly useful for facial animation. They are often considered indispensible
by professional animators working with shape keys.

In-betweens are offered natively in many 3D animation software packages, but not
in Blender. While it is possible to implement them using Blender's existing toolset
it's time-consuming and requires a prior understanding of the mechanics. The
**In-Betweens** addon brings a flexible implementation of in-betweens to Blender
that is easy-to-use while offering advanced features that not only match the
capabilities of other software but exceed them.

**In-Betweens** has been carefully crafted so that it builds the required components
using Blender's native toolset, meaning you can share or sell your creations with
other users without requiring them to install the addon, and integrate the addon
into your pipeline without worrying about compatibility issues.
