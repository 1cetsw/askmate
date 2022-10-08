Array.prototype.random = function (limit) {
        let target = [];
        let source = this;
        let i = 0;
        let n = source.length;
        let index;
        if (typeof limit == 'undefined' || limit < 0) limit = 1;
        else if (!limit) limit = this.length;
        for (; i < limit && n > 0; i++) {
            do {
                index = Math.random();
            } while (index === 1);
            index = Math.floor(index * n);
            target.push(source[index]);
            source[index] = source[--n];
        }
        return target;
    }

    document.write(['”A man’s worth is no greater than the worth of his ambitions.” – Marcus Aurelius',
        '”The people who are crazy enough to think they can change the world are the ones who do.” – Steve Jobs',
        '“There is one weakness in people for which there is no remedy. ' +
        '“It is the universal weakness of lack of ambition.” – Napoleon Hill',
        '“Ambitions reveal direction.” – Mace Windu',
        '“A young man without ambition is an old man waiting to be.” – Steven Brust',
        '“Ambition beats genius 99 percent of the time.” – Jay Leno',
        '“Ambition is a dream with a V8 engine.” – Elvis Presley'].random().join(''));