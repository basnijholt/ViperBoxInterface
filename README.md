<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->



<!-- END doctoc generated TOC please keep comment here to allow auto update -->

��#   >���  V i p e r B o x I n t e r f a c e  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ v i p e r b o x i n t e r f a c e . p n g "   s t y l e = " w i d t h :   5 0 % ;   h e i g h t :   a u t o ; " >  
         < ! - -   < f i g c a p t i o n > O v e r v i e w   o f   a l l   t h e   s e t t i n g s   f o r   o n e   V i p e r B o x < / f i g c a p t i o n >   - - >  
 < / f i g u r e >  
  
  
 >   V i p e r B o x I n t e r f a c e   i s   a   p i e c e   o f   s o f t w a r e   t h a t   s t r e a m l i n e s   i n t e r a c t i o n   w i t h   t h e   V i p e r B o x   d e v e l o p e d   f o r   t h e   N e u r a V i P e R   p r o j e c t .  
 >   I t   s t r e a m s   d a t a   t h r o u g h   [ O p e n   E p h y s ] ( # o p e n - e p h y s ) .  
  
 #   =���  T a b l e   o f   C o n t e n t s  
 < ! - -   T O C   - - >  
  
 -   [ >���  V i p e r B o x I n t e r f a c e ] ( # - v i p e r b o x i n t e r f a c e )  
 -   [ =���  T a b l e   o f   C o n t e n t s ] ( # - t a b l e - o f - c o n t e n t s )  
 -   [ =���  I n s t a l l a t i o n ] ( # - i n s t a l l a t i o n )  
         -   [ M a n u a l   i n s t a l l a t i o n ] ( # m a n u a l - i n s t a l l a t i o n )  
 -   [ =إ��  U s i n g   t h e   G U I ] ( # - u s i n g - t h e - g u i )  
         -   [ S t a r t i n g   u p ] ( # s t a r t i n g - u p )  
                 -   [ V i p e r B o x   C o n t r o l   u s a g e ] ( # v i p e r b o x - c o n t r o l - u s a g e )  
                 -   [ O p e n   E p h y s   G U I   u s a g e ] ( # o p e n - e p h y s - g u i - u s a g e )  
         -   [ R e c o r d i n g ] ( # r e c o r d i n g )  
 -   [ �&�  S e t t i n g s ] ( # s e t t i n g s )  
         -   [ G a i n   s e t t i n g s ] ( # g a i n - s e t t i n g s )  
         -   [ R e f e r e n c e s   a n d   i n p u t   s e t t i n g s ] ( # r e f e r e n c e s - a n d - i n p u t - s e t t i n g s )  
         -   [ C h o o s i n g   p r o b e   e l e c t r o d e s ] ( # c h o o s i n g - p r o b e - e l e c t r o d e s )  
 -   [ S'  F A Q ] ( # - f a q )  
 -   [ >��  U s i n g   t h e   A P I ] ( # - u s i n g - t h e - a p i )  
 -   [ =����  O v e r v i e w   o f   V i p e r B o x   s e t t i n g s ] ( # - o v e r v i e w - o f - v i p e r b o x - s e t t i n g s )  
 -   [ =���  C h a n g i n g   s e t t i n g s   t h r o u g h   X M L   s c r i p t s ] ( # - c h a n g i n g - s e t t i n g s - t h r o u g h - x m l - s c r i p t s )  
         -   [ R e c o r d i n g S e t t i n g s ] ( # r e c o r d i n g s e t t i n g s )  
         -   [ S t i m u l a t i o n   s e t t i n g s ] ( # s t i m u l a t i o n - s e t t i n g s )  
  
 < ! - -   / T O C   - - > y o u   n e e d   t o   c r e a t e   a   c o n d a   e n v i r o n m e n t   n a m e d   ' v i p e r b o x '   a n d   i n s t a l l   t h e   p a c k a g e s   i n   s e t u p / e n v i r o n m e n t . y a m l .   Y o u   c a n   d o   t h i s   b y   r u n n i n g   ` c o n d a   c r e a t e   - - n a m e   v i p e r b o x   - - f i l e   [ p a t h - t o - v i p e r b o x i n t e r f a c e - f o l d e r ] / s e t u p / v i p e r b o x . y a m l ` .    
   N o   s t a r t u p   s h o r t c u t   w i l l   b e   c r e a t e d .  
  
 #   =إ��  U s i n g   t h e   G U I  
  
 T h e   G U I   c a n   b e   u s e d   t o   c o n t r o l   t h e   V i p e r B o x   d i r e c t l y .  
  
 # #   S t a r t i n g   u p  
  
 T h e   i n s t a l l a t i o n   s c r i p t   c r e a t e s   a   s h o r t c u t   o n   t h e   d e s k t o p   c a l l e d   " V i p e r B o x A P I " .   T h r e e   s c r e e n s   w i l l   b e   o p e n e d ;   t h e   V i p e r B o x   C o n t r o l ,   t h e   O p e n   E p h y s   G U I   a n d   a   t e r m i n a l .   I f   t h i s   d i d n ' t   w o r k   o u t   f o r   s o m e   r e a s o n ,   y o u   c a n   a l s o   s t a r t   t h e   s o f t w a r e   b y   n a v i g a t i n g   t o   t h e   f o l d e r   w h e r e   t h e   s o f t w a r e   i s   d o w n l o a d e d   a n d   d o u b l e - c l i c k   s t a r t _ a p p . b a t .  
  
 I f   t h a t   d o e s n ' t   w o r k   ( s e e   [ F A Q ] ( # f a q ) ) ,   y o u   c a n   s t a r t   t h e   s o f t w a r e   b y   f o l l o w i n g   t h e s e   s t e p s   ( a l s o   m a k e   s u r e   y o u   h a v e   t h e   l a t e s t   v e r s i o n   o f   t h e   s o f t w a r e ) :  
 1 .   O p e n   A n a c o n d a   P r o m p t   ( y o u   c a n   f i n d   i t   b y   s e a r c h i n g   f o r   i t   i n   t h e   s t a r t   m e n u )  
 2 .   T y p e   ` c o n d a   a c t i v a t e   v i p e r b o x `   a n d   p r e s s   e n t e r  
 3 .   N a v i g a t e   t o   t h e   f o l d e r   w h e r e   t h e   s o f t w a r e   i s   d o w n l o a d e d   b y   t y p i n g   ` c d   < p a t h   t o   t h e   f o l d e r > `  
 4 .   T y p e   ` u v i c o r n   m a i n : a p p   - - r e l o a d `   a n d   p r e s s   e n t e r  
  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ v i p e r b o x _ g u i . p n g "   s t y l e = " w i d t h :   8 0 % ;   h e i g h t :   a u t o ; " >  
         < f i g c a p t i o n > V i p e r B o x   G U I < / f i g c a p t i o n >  
 < / f i g u r e >  
      
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ o e _ g u i . p n g "   s t y l e = " w i d t h :   8 0 % ;   h e i g h t :   a u t o ; " >  
         < f i g c a p t i o n > O p e n   E p h y s   G U I < / f i g c a p t i o n >  
 < / f i g u r e >  
      
  
 # # #   V i p e r B o x   C o n t r o l   u s a g e  
 I n   * V i p e r B o x   c o n t r o l * ,   y o u   c a n  
 -   C o n n e c t   t o   t h e   V i p e r B o x   a n d   c o n n e c t   t o   O p e n   E p h y s .   T h i s   h a p p e n s   a u t o m a t i c a l l y   w h e n   y o u   s t a r t   t h e   s o f t w a r e .  
 -   C h a n g e   r e c o r d i n g   f i l e   n a m e   a n d   l o c a t i o n   a n d   s t a r t   a n d   s t o p   t h e   a c q u i s i t i o n .   Y o u ' l l   s e e   t h e   r e c o r d e d   d a t a   i n   t h e   O p e n   E p h y s   G U I .   Y o u   c a n   a l s o   s t i m u l a t e   i f   y o u   a r e   r e c o r d i n g .  
 -   U p l o a d   s e t t i n g s   t o   t h e   V i p e r B o x .   Y o u   c a n   e i t h e r   u p l o a d   t h e   r e c o r d i n g   o r   s t i m u l a t i o n   s e t t i n g s   y o u   s e t   i n   t h e   G U I   o r   y o u   c a n   u p l o a d   d e f a u l t   s e t t i n g s .   T h e   d e f a u l t   s e t t i n g s   a r e   l o c a t e d   i n   t h e   ` d e f a u l t s `   f o l d e r .   Y o u   c a n   e d i t   t h e s e   t o   y o u r   l i k i n g .  
  
 I n   * R e c o r d i n g   s e t t i n g s * ,   y o u   c a n   c h a n g e   t h e   r e c o r d i n g   s e t t i n g s .   I n   t h e   I M T E K   p r o b e s   a n d   t h e   s h o r t   w i r e d   M Z I P A ,   o n l y   t h e   b o d y   [ r e f e r e n c e ] ( # r e f e r e n c e s - a n d - i n p u t - s e t t i n g s )   i s   c o n n e c t e d   t o   t h e   A S I C .   T o   u s e   t h e   c o r r e c t   g a i n ,   p l e a s e   r e f e r   t o   [ G a i n   s e t t i n g s ] ( # g a i n - s e t t i n g s ) .   T o   c h a n g e   f r o m   w h i c h   e l e c t r o d e   y o u   w a n t   t o   r e c o r d ,   r e f e r   t o   [ C h o o s i n g   p r o b e   e l e c t r o d e s ] ( # c h o o s i n g - p r o b e - e l e c t r o d e s ) .  
  
 I n   * W a v e f o r m   s e t t i n g s * ,   y o u   c a n   c h a n g e   t h e   s t i m u l a t i o n   w a v e f o r m .  
  
 I n   * P u l s e   p r e v i e w * ,   y o u   c a n   p r e v i e w   t h e   s t i m u l a t i o n   w a v e f o r m   a f t e r   y o u   p r e s s   ` R e l o a d ` .  
  
 I n   * S t i m u l a t i o n   e l e c t r o d e   s e l e c t i o n * ,   y o u   c a n   s e l e c t   f r o m   w h i c h   e l e c t r o d e s   y o u   w a n t   t o   s t i m u l a t e .  
  
 # # #   O p e n   E p h y s   G U I   u s a g e  
 T h e   O p e n   E p h y s   G U I   i s   a n   o p e n - s o u r c e ,   p l u g i n - b a s e d   a p p l i c a t i o n   f o r   a c q u i r i n g   e x t r a c e l l u l a r   e l e c t r o p h y s i o l o g y   d a t a .   I t   w a s   d e s i g n e d   b y   n e u r o s c i e n t i s t s   t o   m a k e   t h e i r   e x p e r i m e n t s   m o r e   f l e x i b l e   a n d   e n j o y a b l e .   T h e   f u l l   d o c u m e n t a t i o n   c a n   b e   f o u n d   [ h e r e ] ( h t t p s : / / o p e n - e p h y s . g i t h u b . i o / g u i - d o c s / U s e r - M a n u a l / E x p l o r i n g - t h e - u s e r - i n t e r f a c e . h t m l ) .  
  
 # #   R e c o r d i n g  
 R e c o r d i n g   c a n   b e   d o n e   i n   t h e   O p e n   E p h y s   i n t e r f a c e .  
  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ r e c o r d i n g _ i n s t r u c t i o n s . p n g "   s t y l e = " w i d t h :   8 0 % ;   h e i g h t :   a u t o ; " >  
         < f i g c a p t i o n > R e c o r d i n g   i n   O p e n   E p h y s < / f i g c a p t i o n >  
 < / f i g u r e >  
  
 D a t a   c a n   b e   s a v e d   i n   b i n a r y ,   O p e n   E p h y s   F o r m a t   a n d   N W B   f o r m a t .   T h e   O p e n   E p h y s   F o r m a t   u s e f u l   f o r   l o a d i n g   t h e   d a t a   i n t o   N e u r o E x p l o r e r   f r o m   w h i c h   i t   c a n   t h e n   b e   e x p o r t e d   i n t o   . N E X   o r   . N E X 5   f o r m a t .   T h e   f o r m a t s   a r e   n o t   a v a i l a b l e   o u t   o f   t h e   b o x ,   t o   i n s t a l l   t h e m ,   p l e a s e   [ f o l l o w   t h e   i n s t r u c t i o n s ] ( h t t p s : / / o p e n - e p h y s . g i t h u b . i o / g u i - d o c s / U s e r - M a n u a l / R e c o r d i n g - d a t a / i n d e x . h t m l ) .  
  
 #   �&�  S e t t i n g s  
 # #   G a i n   s e t t i n g s  
 >   [ ! W A R N I N G ]  
 >   T o   c o r r e c t l y   v i e w   t h e   v o l t a g e   l e v e l s   i n   O p e n   E p h y s ,   t h e   f o l l o w i n g   s c a l i n g   a n d   o f f s e t   n u m b e r s   n e e d   t o   b e   s u p p l i e d   t o   t h e   E p h y s   S o c k e t   i n   O p e n   e p h y s :  
  
 |   G a i n   |   S c a l e   |   O f f s e t   |  
 |   - - - -   |   - - - - -   |   - - - - - -   |  
 |   6 0       |   5 . 6       |   2 0 4 8       |  
 |   2 4       |   1 1 . 2     |   2 0 4 8       |  
 |   1 2       |   1 9 . 8     |   2 0 4 8       |  
  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ e p h y s _ s o c k e t _ s c a l e _ o f f s e t . p n g "   s t y l e = " w i d t h :   3 0 % ;   h e i g h t :   a u t o ; " >  
         < f i g c a p t i o n > S c r e e n s h o t   o f   E p h y s   S o c k e t   i n   O p e n   E p h y s < / f i g c a p t i o n >  
 < / f i g u r e >  
  
 T o   c h a n g e   t h e s e   s e t t i n g s ,   f i r s t   y o u   n e e d   t o   s t o p   t h e   a c q u i s t i o n   o f   d a t a   i n   O p e n   E p h y s   b y   c l i c k i n g   t h e   y e l l o w   p l a y   b u t t o n   i n   t h e   t o p   r i g h t   o f   t h e   s c r e e n .   T h e n   y o u   c a n   c l i c k   ' D I S C O N N E C T '   i n   t h e   E p h y s   S o c k e t   m o d u l e .   A f t e r   t h a t ,   y o u   c a n   c h a n g e   t h e   v a l u e s   i n   t h e   ' S c a l e '   f i e l d .   A f t e r   c h a n g i n g   t h e   v a l u e s ,   g o   t o   t h e   V i p e r B o x   i n t e r f a c e   a n d   c l i c k   ' C o n n e c t   O p e n   E p h y s ' ,   t h e n   c l i c k   ' C O N N E C T '   i n   t h e   E p h y s   S o c k e t   m o d u l e .  
  
 # #   R e f e r e n c e s   a n d   i n p u t   s e t t i n g s  
  
 R e f e r e n c e   s e t t i n g s   a r e   w i r e d   i n   t h e   c h i p   i n   t h e   f o l l o w i n g   w a y .   F o r   e a c h   o f   t h e   6 4   c h a n n e l s   ( o r   a m p l i f i e r s ) ,   o n e   e l e c t r o d e   c a n   b e   c h o s e n   f r o m   a   s e t   o f   4   e l e c t r o d e s .   T h i s   s e t   i s   h a r d w i r e d   a n d   c a n n o t   b e   c h a n g e d .  
  
 T h i s   s i g n a l   i s   c o m p a r e d   t o   a n y   o r   a l l   o f   t h e   r e f e r e n c e s   ( w h i c h   y o u   c a n   s e l e c t   i n   t h e   G U I ) .   I n   p r i n c i p l e ,   t h e   b o d y   r e f e r e n c e   s h o u l d   a l w a y s   b e   u s e d .  
  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ r e f e r e n c e s . p n g "   s t y l e = " w i d t h :   5 0 % ;   h e i g h t :   a u t o ; " >  
         < f i g c a p t i o n > C o n n e c t i o n   o f   r e c o r d i n g   c h a n n e l   ( l e f t )   w i t h   r e c o r d i n g   e l e c t r o d e s   ( t o p   r i g h t )   a n d   r e f e r e n c e s   ( b o t t o m   r i g h t ) < / f i g c a p t i o n >  
 < / f i g u r e >  
  
 # #   C h o o s i n g   p r o b e   e l e c t r o d e s  
  
 W i t h   t h e   I M T E K   p r o b e   a n d   t h e   s h o r t   w i r e d   M Z I P A ,   i t   i s   n o t   p o s s i b l e   t o   r e c o r d   f r o m   a l l   t h e   6 0   e l e c t r o d e s   a t   t h e   s a m e   t i m e .   H o w e v e r ,   i t   i s   p o s s i b l e   t o   s e l e c t   f r o m   w h i c h   e l e c t r o d e   y o u   w a n t   t o   r e c o r d .  
  
 T o   c h a n g e   f r o m   w h i c h   o f   t h e   4   e l e c t r o d e s   y o u   w a n t   t o   r e c o r d   ( a s   m e n t i o n e d   i n   [ R e f e r e n c e s   a n d   i n p u t   s e t t i n g s ] ( # r e f e r e n c e s - a n d - i n p u t - s e t t i n g s ) ) ,   e d i t   t h e   E x c e l   f i l e   i n   t h e   ` d e f a u l t s `   f o l d e r ,   c a l l e d   ` e l e c t r o d e _ m a p p i n g _ s h o r t _ c a b l e s . x l s x ` .    
  
 T h i s   m a p p i n g   i s   s p e c i f i c a l l y   d e s i g n e d   f o r   t h e   4   s h a n k   I M T E K   p r o b e .   T h e   f i r s t   c o l u m n   i s   t h e   e l e c t r o d e   o n   t h e   I M T E K   p r o b e .   Y o u   c a n   c h o o s e   t h e   v a l u e   i n   t h e   ' C h a n n e l   t a k e n '   c o l u m n ,   i t   h a s   t o   b e   s e t   e q u a l   t o   a   v a l u e   i n   o n e   o f   t h e   ' i n p u t   #   c h a n n e l '   c o l u m n s .  
  
 F o r   e x a m p l e ,   y o u   w a n t   P r o b e   e l e c t r o d e   1   t o   b e   c o n n e c t e d   t o   c h a n n e l   5 0 ,   t h e n   i n   ' C h a n n e l   t a k e n ' ,   y o u   c h a n g e   t h e   v a l u e   t o   ` = E 2 ` .   T h i s   w i l l   u p d a t e   t h e   s h e e t   a n d   b u t   y o u   w i l l   s e e   t h a t   P r o b e   e l e c t r o d e   2   n o w   h a s   ' D u p l i c a t e '   i n   t h e   ' D u p l i c a t e '   c o l u m n .   T h i s   m e a n s   t h a t   i t   w o n ' t   b e   p o s s i b l e   t o   r e c o r d   f r o m   P r o b e   e l e c t r o d e   2   a n d   t h e   r e c o r d i n g   w i l l   b e   s e t   t o   0 .  
  
 O n l y   e d i t   t h e   ' C h a n n e l   t a k e n '   c o l u m n .   W h e n e v e r   t h e   s o f t w a r e   s t a r t s   o r   n e w   s e t t i n g s   a r e   u p l o a d e d   t o   t h e   V i p e r B o x ,   t h e   E x c e l   f i l e   w i l l   b e   r e a d   a n d   t h e   s e t t i n g s   w i l l   b e   u p d a t e d .    
  
 N o t e   t h a t   i n   t h e   r e s u l t i n g   r e c o r d i n g   i n   O p e n   E p h y s ,   t h e   ' D u p l i c a t e '   c h a n n e l s   w i l l   b e   s e t   t o   a n   e m p t y   s i g n a l   b u t   t h e i r   o r d e r   i s   t h e   s a m e   a s   o n   t h e   I M T E K   p r o b e .  
  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ e l e c t r o d e _ m a p p i n g _ s h o r t _ c a b l e s . p n g "   s t y l e = " w i d t h :   1 0 0 % ;   h e i g h t :   a u t o ; " >  
         < f i g c a p t i o n > C h a n g i n g   w h i c h   P r o b e   e l e c t r o d e s   w i l l   b e   r e a d   o u t . < / f i g c a p t i o n >  
 < / f i g u r e >  
  
 #   S'  ( F ) A Q  
 -   * * Q * * :   O p e n   E p h y s   d o e s n ' t   s h o w   a n y   d a t a ,   w h a t   c a n   I   d o ?  
         -   * * A * * :   I n   t h e   b o t t o m   l e f t ,   c l i c k   t h e   c o n n e c t   b u t t o n   i n   t h e   s i g n a l   c h a i n   i n   t h e   E p h y s   S o c k e t   m o d u l e .   A f t e r   t h a t ,   c l i c k   t h e   p l a y   b u t t o n   i n   t h e   t o p   r i g h t   o f   t h e   O p e n   E p h y s   w i n d o w .  
 -   * * Q * * :   T h e   s h o r t c u t   i s   n o t   w o r k i n g ,   w h a t   c a n   I   d o ?  
         -   * * A * * :   T h i s   i s   p r o b a b l y   d u e   t o   t h e   f a c t   t h a t   P o w e r S h e l l   d o e s n ' t   h a v e   r i g h t s   a s   t o   e x e c u t e   t h e   s t a r t u p   s c r i p t ,   i n   p a r t i c u l a r ,   t h e   ` c o n d a `   c o m m a n d .   T h e r e   i s   a   w h o l e   S t a c k O v e r f l o w   t h r e a d   a b o u t   t h i s   [ h e r e ] ( h t t p s : / / s t a c k o v e r f l o w . c o m / q u e s t i o n s / 6 4 1 4 9 6 8 0 / h o w - c a n - i - a c t i v a t e - a - c o n d a - e n v i r o n m e n t - f r o m - p o w e r s h e l l ) .   P r o b a b l y   t h e   f o l l o w i n g   m i g h t   h e l p :  
          
                 1 .   O p e n   P o w e r S h e l l   a n d   b r o w s e   t o   ` c o n d a b i n `   f o l d e r   i n   y o u r   C o n d a   i n s t a l l a t i o n   d i r e c t o r y ,   f o r   e x a m p l e :   ` C : \ U s e r s \ < u s e r n a m e > \ a n a c o n d a 3 \ c o n d a b i n `  
                 2 .   R u n   ` . / c o n d a   i n i t   p o w e r s h e l l `   i n   t h a t   f o l d e r ,   a n d   r e o p e n   t h e   P o w e r S h e l l .  
                 3 .   P l e a s e   n o t e :   I f   y o u   e n c o u n t e r e d   ` p s 1   c a n n o t   b e   l o a d e d   b e c a u s e   r u n n i n g   s c r i p t s   i s   d i s a b l e d   o n   t h i s   s y s t e m ` ,   s i m p l y   r u n   t h e   P o w e r S h e l l   a s   A d m i n i s t r a t o r   a n d   e n t e r   t h e   f o l l o w i n g :   ` S e t - E x e c u t i o n P o l i c y   - S c o p e   C u r r e n t U s e r   - E x e c u t i o n P o l i c y   U n r e s t r i c t e d `  
                 4 .   T r y   a g a i n   t o   s t a r t   t h e   s o f t w a r e   b y   d o u b l e - c l i c k i n g   t h e   s h o r t c u t   o n   t h e   d e s k t o p .  
  
 -   * * Q * * :   T h e   s o f t w a r e   i s   n o t   r e s p o n d i n g ,   w h a t   c a n   I   d o ?  
         -   * * A * * :   O f t e n ,   t h e   b e s t   s o l u t i o n   i s   t o   c l o s e   a l l   r u n n i n g   i n s t a n c e s   o f   t h e   s o f t w a r e   a n d   h a r d w a r e .   T h i s   m e a n s   p r e s s i n g   t h e   p o w e r   b u t t o n   o n   t h e   V i p e r B o x   t o   s h u t   i t   d o w n   a n d   c l o s i n g   t h e   s o f t w a r e .   I f   t h e   s o f t w a r e   i s   s t u c k ,   y o u   c a n   g o t   t o   W i n d o w s   T a s k   M a n a g e r   a n d   f i n d   a   p r o c e s s   c a l l e d   ' P y t h o n '   a n d   e n d   i t .   T h e n ,   r e s t a r t   t h e   s o f t w a r e   a n d   t h e   V i p e r B o x .    
         -   N o t e :   i f   y o u   a r e   r u n n i n g   s o m e   o t h e r   P y t h o n   s o f t w a r e ,   y o u   w o n ' t   b e   a b l e   t o   d i s c e r n   b e t w e e n   t h e   t w o .   D o n ' t   s t o p   a   p r o c e s s   i f   t h i s   c a n   c a u s e   p r o b l e m s .  
 -   * * Q * * :   W h a t   d o   t h e   c o l o r s   o f   t h e   L E D ' s   o n   t h e   V i p e r B o x   m e a n ?  
         -   * * A * * :   T h e   L E D ' s   o n   t h e   V i p e r B o x   h a v e   t h e   f o l l o w i n g   m e a n i n g s :  
                 -   V i p e r B o x   p o w e r   b u t t o n   s i d e  
                         -   G r e e n :   t h e   V i p e r B o x   i s   c o n n e c t e d   t o   t h e   c o m p u t e r  
                         -   R e d :   t h e   V i p e r B o x   i s   n o t   c o n n e c t e d   t o   t h e   s o f t w a r e   o r   t h e r e   i s   a n   e r r o r  
                         -   B l u e :   t h e   V i p e r B o x   i s   r e c o r d i n g  
                 -   V i p e r B o x   S e r D e s   s i d e  
                         -   W h i t e :   h e a d s t a g e   c o n n e c t e d   o r   e m u l a t i o n   a c t i v e  
                         -   o f f :   o t h e r w i s e  
  
  
 #   >��  U s i n g   t h e   A P I  
  
 T h e   A P I   c a n   b e   u s e d   t o   c o m m u n i c a t e   w i t h   t h e   V i p e r B o x .   I t   c a n   b e   u s e d   t o   c o n n e c t   t o   t h e   V i p e r B o x ,   u p l o a d   r e c o r d i n g   a n d   s t i m u l a t i o n   s e t t i n g s   a n d   s t a r t   a n d   s t o p   r e c o r d i n g s   a n d   s t i m u l a t i o n s .  
 T h e   A P I   c a n   b e   m a n u a l l y   c o n t r o l l e d   f r o m   t h e   w e b   i n t e r f a c e   b y   c l i c k i n g   t h e   d r o p d o w n   n e x t   t o   t h e   f u n c t i o n ,   t h e n   c l i c k i n g   " T r y   i t   o u t "   a n d   t h e n   c l i c k i n g   t h e   b l u e   " E x e c u t e "   b u t t o n .  
 T h e   t y p i c a l   w o r k f l o w   t o   d o   a   r e c o r d i n g   a n d   s t i m u l a t i o n   i s   t o   r u n   t h e   f o l l o w i n g   c o m m a n d s :  
 -   ` / c o n n e c t ` :   t o   c o n n e c t   t o   t h e   V i p e r B o x  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ c o n n e c t . g i f "   s t y l e = " w i d t h :   8 0 % ;   h e i g h t :   a u t o ; " >  
         < ! - -   < f i g c a p t i o n > O v e r v i e w   o f   a l l   t h e   s e t t i n g s   f o r   o n e   V i p e r B o x < / f i g c a p t i o n >   - - >  
 < / f i g u r e >  
  
 -   ` / u p l o a d _ r e c o r d i n g _ s e t t i n g s ` :   t o   u p l o a d   t h e   r e c o r d i n g   s e t t i n g s .   D e f a u l t   [ X M L   s e t t i n g s ] ( # x m l - s c r i p t s )   a r e   s e l e c t e d   b y   d e f a u l t .  
         -   T o   e d i t   t h e   s e t t i n g s ,   o p e n   a n   e d i t o r   a n d   c o p y   t h e   d e f a u l t   s e t t i n g s   f r o m   t h e   d e f a u l t s   f o l d e r   i n t o   i t .   A d j u s t   t h e m   a n d   c o p y   a n d   p a s t e   e v e r y t h i n g   i n t o   t h e   V i p e r B o x   A P I .   S e e   b e l o w .  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ r e c o r d i n g _ s e t t i n g s . g i f "   s t y l e = " w i d t h :   8 0 % ;   h e i g h t :   a u t o ; " >  
         < ! - -   < f i g c a p t i o n > O v e r v i e w   o f   a l l   t h e   s e t t i n g s   f o r   o n e   V i p e r B o x < / f i g c a p t i o n >   - - >  
 < / f i g u r e >  
  
 -   ` / u p l o a d _ s t i m u l a t i o n _ s e t t i n g s ` :   t o   u p l o a d   t h e   s t i m u l a t i o n   s e t t i n g s .   D e f a u l t   s e t t i n g s   a r e   s e l e c t e d   b y   d e f a u l t .   X M L   s e t t i n g s   c a n   b e   a d d e d   h e r e ,   t o o .  
 -   ` / s t a r t _ r e c o r d i n g ` :   t o   s t a r t   t h e   r e c o r d i n g .   D o n ' t   f o r g e t   t o   g i v e   u p   a   n a m e .  
 -   ` / s t a r t _ s t i m u l a t i o n ` :   t o   s t a r t   t h e   s t i m u l a t i o n .  
 -   ` / s t o p _ r e c o r d i n g ` :   t o   s t o p   t h e   r e c o r d i n g .   T h e   r e c o r d i n g   w i l l   b e   s a v e d   i n   t h e   R e c o r d i n g s   f o l d e r .   T h e   s e t t i n g s   t h a t   y o u   u s e d   t o   r e c o r d   w i l l   b e   s a v e d   i n   t h e   S e t t i n g s   f o l d e r   u n d e r   t h e   s a m e   n a m e   b u t   a s   X M L   f i l e .  
  
 D u r i n g   a   r e c o r d i n g ,   n e w   s t i m u l a t i o n   s e t t i n g s   c a n   b e   u p l o a d e d   a n d   a   n e w   s t i m u l a t i o n   c a n   b e   s t a r t e d .  
  
 >   [ ! W A R N I N G ]  
 >   * * B e f o r e   v e r s i o n   0 . 0 . 4 * * ,   t h e r e   i s   a   p r o b l e m   w i t h   t h e   d r i v e r   t h a t   i s   n e c e s s a r y   t o   c o n n e c t   t o   t h e   V i p e r B o x .   A n   i n c o m p a t i b l e   d r i v e r   i s   i n s t a l l e d   a u t o m a t i c a l l y   o v e r n i g h t .   E v e r y   t i m e   y o u   s t a r t   t h e   V i p e r B o x I n t e r f a c e ,   y o u   n e e d   t o   r e i n s t a l l   t h e   d r i v e r .   T h i s   c a n   b e   d o n e   b y   f o l l o w i n g   t h e s e   s t e p s :  
 >   1 . 	 C o n n e c t   V i p e r B o x   t o   P C   a n d   p o w e r   o n  
 >   2 . 	 N a v i g a t e   t o   s e t u p / D o w n g r a d e F T D I ,   a n d   r u n   t h e   d o w n g r a d e . b a t   b a t c h   f i l e  
 >   3 . 	 P o w e r   c y c l e   V i p e r B o x  
 >   4 . 	 O p t i o n a l l y :   v e r i f y   d r i v e r   v e r s i o n   i n   D e v i c e   M a n a g e r  
  
  
 #   =����  O v e r v i e w   o f   V i p e r B o x   s e t t i n g s  
  
 < f i g u r e   a l i g n = " c e n t e r " >  
         < i m g   s r c = " i m g s \ s e t t i n g s _ m i n d m a p . p n g "   s t y l e = " w i d t h :   8 0 % ;   h e i g h t :   a u t o ; " >  
         < f i g c a p t i o n > O v e r v i e w   o f   a l l   t h e   s e t t i n g s   f o r   o n e   V i p e r B o x < / f i g c a p t i o n >  
 < / f i g u r e >  
  
 -   b o x :   t h e r e   a r e   u p   t o   3   b o x e s  
 -   p r o b e s :   e a c h   b o x   c a n   h a v e   u p   t o   4   p r o b e s   c o n n e c t e d   t o   t h e m  
 -   s t i m u n i t   w a v e f o r m   s e t t i n g s :   d e f i n e   t h e   w a v e f o r m   t h a t   t h e   s t i m u n i t   g e n e r a t e s  
 -   s t i m u n i t   c o n n e c t e d   e l e c t r o d e s :   e a c h   s t i m u n i t   c a n   b e   c o n n e c t e d   t o   a n y   o r   a l l   o f   t h e   1 2 8   e l e c t r o d e s .  
 -   r e c o r d i n g   c h a n n e l s :   e a c h   b o x   h a s   6 4   r e c o r d i n g   c h a n n e l s   t h a t   e a c h   h a v e   s e v e r a l   s e t t i n g s    
  
 #   =���  C h a n g i n g   s e t t i n g s   t h r o u g h   X M L   s c r i p t s  
 T h e   w a y   t o   c o m m u n i c a t e   s e t t i n g s   w i t h   t h e   V i p e r B o x   i s   t h r o u g h   X M L   s c r i p t s .   T h e s e   s c r i p t s   c a n   b e   u s e d   t o   d e f i n e   s e t t i n g s   a n d   t o   s t a r t   a n d   s t o p   r e c o r d i n g   a n d   s t i m u l a t i o n .   T h e   X M L   s c r i p t s   c a n   b e   s e n t   t o   t h e   V i p e r B o x   t h r o u g h   t h e   A P I .  
  
 # #   R e c o r d i n g S e t t i n g s  
 H e r e   i s   a n   e x a m p l e   f o r   s e t t i n g   t h e   r e c o r d i n g   s e t t i n g s   i n   X M L   f o r m a t .   T h e   d e f a u l t   r e c o r d i n g   s e t t i n g s   a r e   t h e   f o l l o w i n g :  
 ` ` ` x m l  
 < ? x m l   v e r s i o n = " 1 . 0 "   e n c o d i n g = " U T F - 8 " ? >  
 < P r o g r a m >  
         < S e t t i n g s >  
                 < R e c o r d i n g S e t t i n g s >  
                         < C h a n n e l   b o x = " - "   p r o b e = " - "   c h a n n e l = " - "   r e f e r e n c e s = " - "   g a i n = " 1 "   i n p u t = " 0 " / >  
                 < / R e c o r d i n g S e t t i n g s >  
         < / S e t t i n g s >  
 < / P r o g r a m >  
 ` ` `  
 I n   t h e   a b o v e   c o d e ,   t h e   d e f a u l t   r e c o r d i n g   s e t t i n g s   a r e   s t o r e d   i n   t h e   ` C h a n n e l `   e l e m e n t .   T h e   f i r s t   p a r t   d e f i n e s   f o r   w h i c h   c o m p o n e n t   t h e   s e t t i n g s   a r e   m e a n t ,   t h e   s e c o n d   p a r t   d e s c r i b e s   t h e   s e t t i n g s .    
 -   ` b o x = " - " `   m e a n s   f o r   a l l   b o x e s   t h a t   a r e   c o n n e c t e d .  
 -   ` p r o b e = " - " `   m e a n s   f o r   a l l   p r o b e s   t h a t   a r e   c o n n e c t e d .  
 -   ` c h a n n e l = " - " `   m e a n s   f o r   a l l   r e c o r d i n g   c h a n n e l s   ( a l w a y s   6 4 ) .  
 -   ` r e f e r e n c e s = " - " `   m e a n s   a l l   [ r e f e r e n c e ] ( # r e f e r e n c e s - a n d - i n p u t - s e t t i n g s ) ,   t h i s   m e a n s   t h e   B o d y   r e f e r e n c e   a n d   r e f e r e n c e s   1 - 8 .  
 -   ` g a i n = " 1 " `   m e a n s   t h e   c h a n n e l   [ g a i n ] ( # g a i n - s e t t i n g s ) .   T h e   p o s s i b l e   v a l u e s   a r e :  
         -   " 0 " :   x   6 0  
         -   " 1 " :   x   2 4  
         -   " 2 " :   x   1 2  
 -   ` i n p u t = " 0 " `   m e a n s   w h i c h   [ i n p u t ] ( # c h o o s i n g - p r o b e - e l e c t r o d e s )   e l e c t r o d e   s h o u l d   b e   c o n n e c t e d   t o   t h e   r e c o r d i n g   c h a n n e l .  
  
 Y o u   c a n   a l s o   s p e c i f y   t h e   s e t t i n g s   m o r e   p r e c i s e l y .   F o r   e x a m p l e ,   i f   y o u   w a n t   r e c o r d i n g   c h a n n e l s   1 ,   6 ,   7   a n d   8   t o   h a v e   f e w e r   r e f e r e n c e s ,   n a m e l y   o n l y   r e f e r e n c e   ' b '   ( b o d y )   a n d   ' 3 ' :  
 ` ` ` x m l  
 < ? x m l   v e r s i o n = " 1 . 0 "   e n c o d i n g = " U T F - 8 " ? >  
 < P r o g r a m >  
         < S e t t i n g s >  
                 < R e c o r d i n g S e t t i n g s >  
                         < C h a n n e l   b o x = " - "   p r o b e = " - "   c h a n n e l = " - "   r e f e r e n c e s = " - "   g a i n = " 1 "   i n p u t = " 0 " / >  
                         < C h a n n e l   b o x = " - "   p r o b e = " - "   c h a n n e l = " 1 , 6 - 8 "   r e f e r e n c e s = " b , 3 "   g a i n = " 1 "   i n p u t = " 0 " / >  
                 < / R e c o r d i n g S e t t i n g s >  
         < / S e t t i n g s >  
 < / P r o g r a m >  
 ` ` `  
 I n   t h e   a b o v e   c a s e ,   t h e   f i r s t   l i n e   w i l l   b e   l o a d e d   t o   t h e   V i p e r B o x   f i r s t   a n d   t h e n   t h e   l a t t e r   c h a n n e l   s e t t i n g s   w i l l   b e   o v e r w r i t t e n   t o   t h e   s p e c i f i c   c h a n n e l s .  
  
 # #   S t i m u l a t i o n   s e t t i n g s  
 T h e   d e f a u l t   s t i m u l a t i o n   s e t t i n g s   a r e   t h e   f o l l o w i n g :  
 ` ` ` x m l  
 < ? x m l   v e r s i o n = " 1 . 0 "   e n c o d i n g = " U T F - 8 " ? >  
 < P r o g r a m >  
         < S e t t i n g s >  
                 < S t i m u l a t i o n W a v e f o r m S e t t i n g s >  
                         < C o n f i g u r a t i o n   b o x = " - "   p r o b e = " - "   s t i m u n i t = " - "   p o l a r i t y = " 0 "   p u l s e s = " 2 0 "   p r e p h a s e = " 0 "  
                                 a m p l i t u d e 1 = " 5 "   w i d t h 1 = " 1 7 0 "   i n t e r p h a s e = " 6 0 "   a m p l i t u d e 2 = " 5 "   w i d t h 2 = " 1 7 0 "  
                                 d i s c h a r g e = " 2 0 0 "   d u r a t i o n = " 6 0 0 "   a f t e r t r a i n = " 1 0 0 0 "   / >  
                 < / S t i m u l a t i o n W a v e f o r m S e t t i n g s >  
                 < S t i m u l a t i o n M a p p i n g S e t t i n g s >  
                         < M a p p i n g   b o x = " - "   p r o b e = " - "   s t i m u n i t = " - "   e l e c t r o d e s = " - "   / >  
                 < / S t i m u l a t i o n M a p p i n g S e t t i n g s >  
         < / S e t t i n g s >  
 < / P r o g r a m >  
 ` ` `  
 I n   S t i m u l a t i o n W a v e f o r m S e t t i n g s ,   ` s t i m u n i t `   m e a n s   s t i m u l a t i o n   u n i t   w h i c h   i s   a   w a v e f o r m   g e n e r a t o r ,   t h e r e   a r e   8   s t i m u l a t i o n   u n i t s   p e r   p r o b e .  
 I n   S t i m u l a t i o n M a p p i n g S e t t i n g s ,   t h e s e   s t i m u l a t i o n   u n i t s   c a n   b e   c o n n e c t e d   t o   a n y   o r   a l l   o f   t h e   e l e c t r o d e s .  
  
 < f i g u r e >  
         < i m g   s r c = " i m g s \ s t i m u l a t i o n _ t i m i n g . p n g "   s t y l e = " w i d t h :   9 0 % ;   h e i g h t :   a u t o ; " >  
         < f i g c a p t i o n   a l i g n = " c e n t e r " > S t i m u l a t i o n   t i m i n g < / f i g c a p t i o n >  
 < / f i g u r e >  
  
 T h e   p o s s i b l e   p a r a m e t e r s   f o r   t h e   s t i m u l a t i o n   u n i t s   a r e :  
  
 |   S e t t i n g             |   D e s c r i p t i o n                                                                                             |   U n i t         |   R a n g e           |   S t e p   s i z e   |   D e f a u l t   |  
 |   - - - - - - - - - - - -   |   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -   |   - - - - - - -   |   - - - - - - - - -   |   - - - - - - - - -   |   - - - - - - -   |  
 |   ` p o l a r i t y `       |   P o l a r i t y   o f   t h e   s t i m u l a t i o n   w a v e f o r m                                           |   b o o l e a n   |   0 - 1               |   1                   |   0               |  
 |   ` p u l s e s `           |   N u m b e r   o f   p u l s e s   i n   t h e   w a v e f o r m                                                   |   n u m b e r     |   1 - 2 5 5           |   1                   |   2 0             |  
 |   ` p r e p h a s e `       |   T i m e   i n   m i c r o s e c o n d s   b e f o r e   t h e   f i r s t   p u l s e                             |   �s             |   1 0 0 - 2 5 5 0 0   |   1 0 0               |   0               |  
 |   ` a m p l i t u d e 1 `   |   A m p l i t u d e   o f   t h e   f i r s t   p h a s e                                                           |   �A             |   0 - 2 5 5           |   1                   |   5               |  
 |   ` w i d t h 1 `           |   W i d t h   o f   t h e   f i r s t   p h a s e                                                                   |   �s             |   1 0 - 2 5 5 0       |   1 0                 |   1 7 0           |  
 |   ` i n t e r p h a s e `   |   T i m e   b e t w e e n   t h e   f i r s t   a n d   s e c o n d   p h a s e                                     |   �s             |   1 0 - 2 5 5 0 0     |   1 0                 |   6 0             |  
 |   ` a m p l i t u d e 2 `   |   A m p l i t u d e   o f   t h e   s e c o n d   p h a s e                                                         |   �A             |   0 - 2 5 5           |   1                   |   5               |  
 |   ` w i d t h 2 `           |   W i d t h   o f   t h e   s e c o n d   p h a s e                                                                 |   �s             |   1 0 - 2 5 5 0       |   1 0                 |   1 7 0           |  
 |   ` d i s c h a r g e `     |   T i m e   i n   m i c r o s e c o n d s   a f t e r   t h e   l a s t   p u l s e                                 |   �s             |   1 0 0 - 2 5 5 0 0   |   1 0 0               |   2 0 0           |  
 |   ` d u r a t i o n `       |   D u r a t i o n   o f   t h e   e n t i r e   t r a i n                                                           |   �s             |   1 0 0 - 2 5 5 0 0   |   1 0 0               |   6 0 0           |  
 |   ` a f t e r t r a i n `   |   T i m e   i n   m i c r o s e c o n d s   a f t e r   t h e   e n t i r e   t r a i n   h a s   f i n i s h e d   |   �s             |   1 0 0 - 2 5 5 0 0   |   1 0 0               |   1 0 0 0         |  
  
  
  
 < ! - -   # #   X M L   c o n t r o l   s c r i p t s  
 X M L   s c r i p t s   c a n   h a v e   f u l l   o r   p a r t i a l   c o n t r o l   o v e r   t h e   V i p e r B o x .   T h e y   c a n   b e   u s e d   f o r :  
 -   d e f i n i n g   s e t t i n g s  
 -   s t a r t i n g   a n d   s t o p p i n g   r e c o r d i n g   a n d   s t i m u l a t i o n  
  
 T h e   f o r m a t   i s   a s   f o l l o w s :  
 ` ` ` x m l  
 < P r o g r a m >  
         < S e t t i n g s >  
                 < R e c o r d i n g S e t t i n g s >  
                         < C h a n n e l   b o x = " - "   p r o b e = " - "   c h a n n e l = " - "   r e f e r e n c e s = " 1 0 0 0 0 0 0 0 0 "   g a i n = " 1 "   i n p u t = " 0 "   / >  
                 < / R e c o r d i n g S e t t i n g s >  
                 < S t i m u l a t i o n W a v e f o r m S e t t i n g s >  
                         < C o n f i g u r a t i o n   b o x = " - "   p r o b e = " - "   s t i m u n i t = " - "   p o l a r i t y = " 0 "   p u l s e s = " 2 0 "  
                                 p r e p h a s e = " 0 "   a m p l i t u d e 1 = " 1 "   w i d t h 1 = " 1 7 0 "   i n t e r p h a s e = " 6 0 "   a m p l i t u d e 2 = " 1 "   w i d t h 2 = " 1 7 0 "  
                                 d i s c h a r g e = " 2 0 0 "   d u r a t i o n = " 6 0 0 "   a f t e r t r a i n = " 1 0 0 0 "   / >  
                 < / S t i m u l a t i o n W a v e f o r m S e t t i n g s >  
                 < S t i m u l a t i o n M a p p i n g S e t t i n g s >  
                         < M a p p i n g   b o x = " - "   p r o b e = " - "   s t i m u n i t = " - "   e l e c t r o d e s = " - "   / >  
                 < / S t i m u l a t i o n M a p p i n g S e t t i n g s >  
         < / S e t t i n g s >  
 < / P r o g r a m >  
 ` ` `  
  
 A s   c a n   b e   s e e n   f r o m   t h e   s a m p l e ,   a t   t h e   h i g h e s t   l e v e l   t h e r e   i s   t h e   p r o g r a m   e l e m e n t .   B e l o w   t h a t   t h e r e   a r e   s e t t i n g s   o r   i n s t r u c t i o n s .   I n   s e t t i n g s   t h e r e   a r e   R e c o r d i n g S e t t i n g s ,   S t i m u l a t i o n W a v e f o r m S e t t i n g s   a n d   S t i m u l a t i o n M a p p i n g   s e t t i n g s .   - - >  
  
  
 < ! - -   #   =�h� =ػ�  R e l a t e d   s o f t w a r e  
 # #   O p e n   E p h y s  
 V i p e r B o x I n t e r f a c e   u s e s   O p e n   E p h y s   t o   s h o w   t h e   r e c o r d e d   d a t a .   P l e a s e   r e f e r   t o   t h e   d o c u m e n t a t i o n    
 o f   O p e n   E p h y s   f o r   i n s t r u c t i o n s   o n   h o w   t o   u s e   i t .   I t   h a s   v a r i o u s   p o s s i b i l i t i e s   t o   v i s u a l i z e   a n d    
 a n a l y z e   t h e   d a t a .   T h e   d o c u m e n t a t i o n   c a n   b e   f o u n d   [ h e r e ] ( h t t p s : / / o p e n - e p h y s . g i t h u b . i o / g u i - d o c s / U s e r - M a n u a l / E x p l o r i n g - t h e - u s e r - i n t e r f a c e . h t m l ) .   - - >  
  
 < ! - -   # #   A n a c o n d a  
 A n a c o n d a   i s   u s e d   t o   s e t   u p   a n d   r u n   t h e   P y t h o n   e n v i r o n m e n t   t h a t   i s   n e e d e d   f o r   t h e    
 V i p e r B o x I n t e r f a c e   t o   r u n .  
  
 # #   G i t  
 G i t   i s   u s e d   t o   d o w n l o a d   t h e   l a t e s t   v e r s i o n   o f   t h e   s o f t w a r e .   - - >  
 