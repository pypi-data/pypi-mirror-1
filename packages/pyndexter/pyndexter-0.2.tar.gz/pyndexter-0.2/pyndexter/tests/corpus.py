# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Alec Thomas <alec@swapoff.org>
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

from pyndexter import Document, URI

# Text thanks to the Lorem Ipsum generator at http://www.lipsum.com/

corpus = [
u"""Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Nunc congue odio
eget risus. Sed convallis velit vel elit. Curabitur ante. Aliquam a purus.
Donec pulvinar. Vestibulum leo purus, egestas quis, dapibus non, tempus ac,
risus. Etiam pretium risus a libero. Integer at dolor sed dolor aliquam
lobortis. Nullam sed libero at sem vehicula placerat. Donec dolor purus,
faucibus sit amet, dictum non, feugiat eget, odio. Nullam ut sem cursus lorem
porttitor tincidunt. Vestibulum a sem. Class aptent taciti sociosqu ad litora
torquent per conubia nostra, per inceptos hymenaeos. Vestibulum pellentesque.
Nulla molestie dolor non mauris. Quisque iaculis. Vestibulum fermentum ultrices
pede. Mauris vulputate sapien ac dolor.""",

u"""Nunc massa nisi, fringilla ut, convallis ac, sodales a, felis. Aenean erat
lectus, sagittis in, ullamcorper eu, placerat vel, lorem. Etiam dui. Duis
vestibulum placerat sem. Suspendisse in eros. Pellentesque erat purus, semper
auctor, ultrices ac, fermentum in, libero. Etiam accumsan velit in dolor. Ut
cursus leo et elit. Cras est. Praesent sapien.""",

u"""Pellentesque augue est, condimentum sodales, vehicula tincidunt, ultrices
quis, mi. Suspendisse quis velit eu ipsum auctor iaculis. Aenean vestibulum
scelerisque tortor. Pellentesque tincidunt. Ut purus sapien, egestas nec,
posuere sit amet, ullamcorper in, elit. Praesent dapibus molestie quam.
Phasellus sed sapien. In hac habitasse platea dictumst. Quisque consectetuer
elementum dolor. Aenean elementum tellus sed erat. Maecenas odio. Proin a dui.
Phasellus felis. Aenean nunc urna, sollicitudin tristique, volutpat quis,
mattis eget, sem.""",

u"""Morbi lacinia sodales quam. Maecenas nunc. Phasellus mollis nibh sit amet
lacus. Etiam pharetra. Vivamus diam ipsum, luctus et, luctus nec, auctor vel,
tellus. Vestibulum lobortis feugiat dolor. Phasellus diam felis, commodo vitae,
laoreet ac, euismod sit amet, nunc. Vestibulum ut metus. Praesent vel nibh ac
libero convallis imperdiet. Morbi dignissim. Donec id purus at lorem lobortis
pretium. Integer massa justo, auctor quis, condimentum vel, feugiat sit amet,
arcu. Nunc lacinia, lectus eget accumsan imperdiet, nunc augue condimentum mi,
in varius ante mi at justo. Sed mauris turpis, porta eget, mollis eu, tempor
sollicitudin, tellus. Sed laoreet aliquet leo. In sapien est, bibendum non,
tempor vel, iaculis at, leo.""",

u"""Integer ligula massa, gravida vel, suscipit eget, pulvinar a, eros. Fusce
vestibulum risus sed massa. Cras dictum eleifend justo. Sed et metus vel neque
faucibus pulvinar. Vivamus tellus mi, rhoncus ut, venenatis eget, sollicitudin
at, diam. Sed sit amet lacus nonummy metus sollicitudin cursus. Fusce a velit.
Etiam eu quam. Pellentesque vulputate pede eget velit. Donec augue lorem,
elementum sed, ornare vitae, ullamcorper sit amet, justo. Maecenas suscipit
velit id turpis. Aenean cursus facilisis mi. Donec id ligula at velit fermentum
ornare. Nullam nec orci. Curabitur vitae nulla sit amet lacus viverra
vestibulum. Lorem ipsum dolor sit amet, consectetuer adipiscing elit.""",

u"""Mauris ac mi. In tincidunt, sapien id cursus tincidunt, ipsum mauris
imperdiet lectus, sed iaculis quam dolor eu metus. Suspendisse mattis. Donec
nec augue vitae nulla aliquam commodo. Nulla ornare lorem ut mauris. Curabitur
massa. Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Ut
pellentesque nunc. Aliquam dapibus pretium dui. Proin dictum ligula scelerisque
nisi. Suspendisse potenti. Quisque ut velit rhoncus orci placerat suscipit. In
tempus, ante vel tempus venenatis, nunc lectus vehicula lectus, vitae vehicula
leo lectus ut lacus. Donec dictum, nisi eu fringilla pharetra, erat tellus
lobortis sem, vitae consectetuer magna nisl vel sem. Morbi ullamcorper augue
sed enim. Fusce rhoncus lacinia turpis. Donec at erat. Nunc vehicula.""",

u"""Cras at eros. Integer risus. Donec a elit eget nisi auctor malesuada.
Integer eu augue. Nam nunc. Nam nec turpis. Suspendisse potenti. Ut interdum
nisi vitae diam. Phasellus sed justo vel lorem malesuada elementum. Cras tempor
urna vitae metus ultricies facilisis. Aliquam erat volutpat. Nulla
facilisi.""",

u"""Integer id sapien. Quisque non arcu. Fusce metus elit, ultricies ac, gravida
tempor, dapibus nec, neque. Aliquam at felis et turpis scelerisque posuere.
Maecenas aliquet quam id odio egestas lacinia. Suspendisse tempor quam euismod
magna. Ut magna sem, hendrerit sed, sodales vel, convallis in, dolor. Ut
molestie ligula eu ligula. Proin quis lacus tincidunt nunc pellentesque
sollicitudin. Aenean pellentesque. Nulla facilisi. Ut sed nibh. Nunc felis
velit, tincidunt sed, mattis id, pharetra eget, dolor. Cras pulvinar mi in
pede.""",

u"""Vestibulum interdum. Quisque dictum vestibulum purus. Sed sed nisl.
Suspendisse potenti. Curabitur in lectus. Nulla et arcu at tellus imperdiet
facilisis. Donec hendrerit aliquam quam. Etiam felis libero, porta ut, luctus
sit amet, varius nec, ante. Cum sociis natoque penatibus et magnis dis
parturient montes, nascetur ridiculus mus. Donec volutpat dolor sed velit. Nunc
sed felis quis lectus gravida dignissim. Donec a augue. Nullam in diam quis
risus tristique vehicula. Sed accumsan. Proin lacus tortor, tincidunt eget,
ornare id, interdum eu, enim. Duis eu orci nec elit consequat imperdiet. Cum
sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus
mus. Vestibulum magna eros, ultrices et, dictum eget, rhoncus in, libero. Ut
eget nunc. Donec et lorem.""",

u"""Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere
cubilia Curae; Quisque posuere dui at tellus. Nam sodales condimentum velit.
Mauris pulvinar leo. Etiam eu dui. Mauris aliquam dignissim mi. Fusce venenatis
urna vel nunc. Praesent imperdiet dolor id metus. Sed ut magna vel turpis
dictum elementum. Fusce nunc dolor, lacinia ut, dignissim quis, gravida
accumsan, purus. In dictum augue. Ut non eros id nisl mollis pretium.""",

u"""Nunc ultricies neque tempor nisi. Etiam congue lectus ac felis. Nam ut dolor
placerat nisi venenatis dictum. Morbi quis turpis in massa vestibulum
consectetuer. Nulla facilisi. Maecenas rhoncus, dolor at sodales pretium, dui
justo dictum nunc, vel condimentum augue nisi a sapien. Sed tincidunt dictum
elit. Aliquam quam pede, semper vitae, porttitor quis, hendrerit ac, nulla.
Nulla porta diam. In lorem urna, ultricies vel, porttitor et, ultricies mattis,
risus. Sed lobortis magna ut lorem. Donec a mi. Duis pretium est dignissim
lorem. Nunc gravida vulputate pede. Ut rutrum adipiscing sem. Praesent sed erat
in tellus commodo volutpat. Curabitur volutpat nisi eget nunc. Proin enim.
Morbi facilisis ante quis purus.""",

u"""Quisque rutrum risus vel est. Morbi ac mi in augue lacinia luctus. Phasellus
eros dui, ornare at, accumsan et, commodo quis, diam. Curabitur dolor risus,
auctor et, auctor sed, lacinia sed, tellus. Nullam lacinia pharetra dui. Donec
eu arcu. Sed adipiscing nisi ut dui blandit eleifend. Duis vel sapien sed felis
lacinia sodales. Donec consequat risus vel quam. Nulla facilisi. Praesent
ornare est at libero. Aliquam risus elit, dignissim vehicula, faucibus a,
accumsan sed, nisi. Etiam nibh. Nullam adipiscing mauris non augue. Vestibulum
ipsum mauris, cursus id, ornare in, molestie non, diam. Curabitur sed quam.
Proin ut libero. Aenean hendrerit est nec felis.""",

u"""Morbi lobortis, urna ut gravida dictum, nisl diam posuere augue, non
suscipit mi turpis id dolor. Phasellus fringilla, augue et imperdiet hendrerit,
justo tortor tincidunt lectus, in gravida enim elit eu nisl. Suspendisse dictum
tellus placerat arcu. Aliquam faucibus massa vitae pede. Curabitur sapien
libero, sodales sit amet, euismod sit amet, ultricies sed, leo. Vivamus cursus
congue arcu. Aliquam erat volutpat. Sed arcu velit, tempor at, posuere in,
dignissim nec, urna. Etiam mollis bibendum orci. Vestibulum augue metus,
interdum ut, imperdiet ac, rutrum vitae, lorem. Nam viverra. Vivamus neque.
Maecenas aliquam fermentum elit. Vestibulum a tellus. Etiam eget nibh sed arcu
convallis luctus. Nullam suscipit. Suspendisse congue. Etiam luctus
consectetuer tellus. Etiam purus magna, egestas id, pharetra id, ullamcorper
quis, erat.""",

u"""Morbi quis tortor a libero tempus pellentesque. Maecenas eu pede vel purus
varius sollicitudin. Nulla suscipit est at turpis. Sed pede. Pellentesque
lectus lectus, sodales nec, ultrices non, adipiscing vel, orci. Donec fermentum
convallis lacus. Donec iaculis risus ultrices arcu. Aliquam urna orci, viverra
sit amet, dictum eu, facilisis at, dui. Proin quis augue. Cras nulla mauris,
dapibus eu, sagittis sed, ultricies non, est. Suspendisse consectetuer. Sed
velit. Nunc lorem tortor, vestibulum vel, aliquet vel, condimentum vitae, elit.
Sed sit amet pede non libero lobortis tempor. Mauris magna.""",

u"""Proin velit. Aliquam erat volutpat. In ornare. Ut mi. Proin sit amet pede
tempus nulla dapibus iaculis. Nulla tincidunt. Etiam sagittis imperdiet mi.
Phasellus elit tellus, mollis sed, mattis at, facilisis et, nulla. Vestibulum
congue fringilla tortor. Ut justo arcu, varius a, vehicula id, mollis sed,
justo. In vehicula, metus ac scelerisque pharetra, eros arcu viverra purus, sit
amet molestie lorem diam a magna. Aenean at sapien. Quisque hendrerit. Sed arcu
est, posuere quis, hendrerit ac, pretium non, pede. Cras accumsan lectus sed
nisl. Integer massa ante, dictum aliquet, ultricies sit amet, ornare vitae,
orci. Nullam interdum blandit ante. Vestibulum leo. Integer sit amet sem.""",

u"""Ut mi tellus, scelerisque id, laoreet eget, interdum sit amet, justo. Etiam
urna. Integer non erat a dui ullamcorper imperdiet. Fusce et tellus ut pede
mattis laoreet. Suspendisse aliquam feugiat nulla. Maecenas in diam eget neque
lobortis ultrices. Morbi in libero nec sem vehicula imperdiet. Mauris sapien
ante, malesuada sit amet, rutrum sed, consequat iaculis, massa. Donec ac velit.
In volutpat odio at justo. Maecenas id lectus. Ut porta. Suspendisse purus.
Proin imperdiet turpis et nibh. Nulla facilisi. Quisque imperdiet est id erat
tempor tincidunt. Phasellus lacinia elit nec turpis.""",

u"""Nulla elit erat, fermentum ut, tempor nec, varius quis, quam. Lorem ipsum
dolor sit amet, consectetuer adipiscing elit. Pellentesque auctor magna vitae
erat. Vivamus sodales. Praesent felis sapien, hendrerit quis, pharetra sit
amet, congue in, lacus. Fusce viverra. Duis venenatis leo at erat. Vivamus eu
ante. Nulla a felis. Sed lacinia nonummy tortor. Proin justo arcu, vulputate
id, gravida iaculis, posuere id, pede. Integer tristique. Etiam varius, nisi
vitae varius aliquet, pede diam feugiat metus, non nonummy ipsum nulla sed
urna. Nullam eu quam. Phasellus vestibulum.""",

u"""Nullam posuere pretium augue. Nulla sed lacus sed nunc mollis imperdiet.
Donec nibh metus, placerat ac, consectetuer quis, tincidunt id, erat.
Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere
cubilia Curae; Nunc feugiat tristique sem. Aenean eros. Donec venenatis. Nulla
sed nibh in orci bibendum condimentum. Donec sed sapien sed quam pulvinar
convallis. Sed rutrum laoreet turpis. Etiam adipiscing lectus sit amet odio.
Mauris eget dolor. Sed aliquet gravida mauris.""",

u"""Phasellus ultrices augue. Aenean eu pede at risus rutrum sodales. Morbi erat
ipsum, ornare ac, dapibus vel, viverra quis, est. Duis in libero ac turpis
nonummy sodales. Ut sit amet magna. Phasellus vitae est. Morbi molestie, tortor
eget lobortis egestas, neque justo aliquet arcu, in posuere libero urna eu
arcu. Vestibulum sit amet est tristique ligula fringilla dapibus. Vestibulum
ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae;
Sed in mi. Cras sed odio. Duis ut orci. Etiam mattis pretium risus. Phasellus
porttitor orci sit amet augue. Phasellus placerat, mauris quis mattis eleifend,
dolor nibh lacinia quam, interdum ornare leo erat ut tellus. Vestibulum ornare
congue nibh. Vivamus tincidunt nisi. Donec rutrum dapibus felis.""",

u"""Donec nisl. Nullam sollicitudin felis vitae tortor. Pellentesque leo diam,
facilisis eget, fermentum eu, scelerisque vitae, enim. Proin vestibulum, orci
in convallis tempus, turpis mauris condimentum sem, a vestibulum leo dolor
vitae eros. Curabitur sagittis. In sed metus. In non nunc eget purus dapibus
vehicula. In mattis, mauris vitae dictum fermentum, justo sem aliquam ligula,
viverra facilisis nisi pede et mi. Donec dapibus, magna iaculis accumsan
vulputate, elit lectus adipiscing nisi, ut adipiscing libero mi id velit. Nunc
feugiat metus eu ligula varius fermentum. Morbi lacinia, nulla et luctus
auctor, ipsum ligula malesuada sem, eget dignissim augue sem eget augue.""",
]

documents = dict([(u'mock://%i' % index,
                  Document(uri=u'mock://%i' % index, content=text,
                           changed=index))
                  for index, text in enumerate(corpus)])

mock_uri_list = [URI(u'mock://%i' % i) for i, doc in enumerate(documents)]
mock_uri_list.sort()

simple_hits = [URI(u'mock://0'), URI(u'mock://1'), URI(u'mock://10'),
               URI(u'mock://12'), URI(u'mock://13'), URI(u'mock://14'),
               URI(u'mock://16'), URI(u'mock://3'), URI(u'mock://4'),
               URI(u'mock://5'), URI(u'mock://6'), URI(u'mock://8')]
simple_query = u'lorem'

and_hits = [URI(u'mock://0'), URI(u'mock://16'), URI(u'mock://3'),
            URI(u'mock://4'), URI(u'mock://5')]
and_query = u'lorem ipsum'

not_hits = [URI(u'mock://16'), URI(u'mock://3'), URI(u'mock://4')]
not_query = u'lorem ipsum -placerat'
